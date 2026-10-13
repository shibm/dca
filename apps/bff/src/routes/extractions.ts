import { Router, Response } from 'express';
import { pool } from '../db.js';
import { AuthRequest, authenticateToken } from '../middleware/auth.js';

export const extractionsRouter = Router();

/**
 * Human-in-the-Loop: Correct an extracted field value with full audit logging
 */
extractionsRouter.patch('/:id', authenticateToken, async (req: AuthRequest, res: Response) => {
  const { id } = req.params;
  const { value, reason } = req.body;

  if (value === undefined) {
    return res.status(400).json({ error: 'New field value is required.' });
  }

  const client = await pool.connect();
  try {
    await client.query('BEGIN');

    // 1. Fetch existing extraction
    const currentRes = await client.query(
      'SELECT id, document_id, field_value FROM document_extractions WHERE id = $1',
      [id]
    );

    if (currentRes.rows.length === 0) {
      await client.query('ROLLBACK');
      return res.status(404).json({ error: 'Extraction not found.' });
    }

    const extraction = currentRes.rows[0];
    const previousValue = extraction.field_value;

    // 2. Update the field value and mark as corrected
    const updateRes = await client.query(
      `UPDATE document_extractions 
       SET field_value = $1, is_corrected = TRUE, validation_status = 'VALID', updated_at = NOW()
       WHERE id = $2
       RETURNING *`,
      [value, id]
    );

    // 3. Insert audit log entry
    await client.query(
      `INSERT INTO extraction_audit_logs (
         extraction_id, document_id, user_id, previous_value, new_value, reason
       ) VALUES ($1, $2, $3, $4, $5, $6)`,
      [id, extraction.document_id, req.user?.id, previousValue, value, reason || 'Manual review correction']
    );

    await client.query('COMMIT');
    return res.json({
      message: 'Extraction updated and audit trail recorded.',
      extraction: updateRes.rows[0],
    });
  } catch (err: any) {
    await client.query('ROLLBACK');
    console.error('Error updating extraction:', err);
    return res.status(500).json({ error: 'Failed to update extraction.' });
  } finally {
    client.release();
  }
});

/**
 * Finalize review and mark document as APPROVED
 */
extractionsRouter.post('/documents/:id/approve', authenticateToken, async (req: AuthRequest, res: Response) => {
  const { id } = req.params;

  try {
    const result = await pool.query(
      `UPDATE documents 
       SET status = 'APPROVED', updated_at = NOW()
       WHERE id = $1
       RETURNING id, file_name, status, updated_at`,
      [id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Document not found.' });
    }

    return res.json({
      message: 'Document successfully approved.',
      document: result.rows[0],
    });
  } catch (err: any) {
    console.error('Error approving document:', err);
    return res.status(500).json({ error: 'Failed to approve document.' });
  }
});

