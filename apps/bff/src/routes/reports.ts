import { Router, Response } from 'express';
import { pool } from '../db.js';
import { AuthRequest, authenticateToken } from '../middleware/auth.js';

export const reportsRouter = Router();

/**
 * Stakeholder Metrics & Summary Dashboard
 */
reportsRouter.get('/summary', authenticateToken, async (_req: AuthRequest, res: Response) => {
  try {
    // 1. Overall counts
    const countsRes = await pool.query(`
      SELECT 
        COUNT(*) as total_documents,
        COUNT(*) FILTER (WHERE status = 'APPROVED') as approved_count,
        COUNT(*) FILTER (WHERE status = 'NEEDS_REVIEW') as needs_review_count,
        COUNT(*) FILTER (WHERE status = 'PROCESSING') as processing_count
      FROM documents
    `);

    // 2. Document type breakdown
    const typeRes = await pool.query(`
      SELECT document_type, COUNT(*) as count 
      FROM documents 
      GROUP BY document_type
    `);

    // 3. Average confidence score across all extractions
    const confRes = await pool.query(`
      SELECT 
        ROUND(AVG(confidence_score)::numeric, 4) as avg_confidence,
        COUNT(*) FILTER (WHERE is_corrected = TRUE) as total_corrected_fields
      FROM document_extractions
    `);

    return res.json({
      metrics: countsRes.rows[0],
      documentTypes: typeRes.rows,
      accuracy: confRes.rows[0],
    });
  } catch (err: any) {
    console.error('Error fetching summary report:', err);
    return res.status(500).json({ error: 'Failed to generate summary report.' });
  }
});

/**
 * Export Extracted Contract Data as CSV
 */
reportsRouter.get('/export-csv', authenticateToken, async (_req: AuthRequest, res: Response) => {
  try {
    const query = `
      SELECT 
        d.id as document_id,
        d.file_name,
        d.document_type,
        d.status,
        MAX(CASE WHEN e.field_key = 'effective_date' THEN e.field_value END) as effective_date,
        MAX(CASE WHEN e.field_key = 'total_contract_value' THEN e.field_value END) as contract_value,
        MAX(CASE WHEN e.field_key = 'governing_law' THEN e.field_value END) as governing_law,
        d.created_at
      FROM documents d
      LEFT JOIN document_extractions e ON d.id = e.document_id
      GROUP BY d.id, d.file_name, d.document_type, d.status, d.created_at
      ORDER BY d.created_at DESC
    `;

    const result = await pool.query(query);

    // Format CSV
    const headers = ['Document ID', 'File Name', 'Type', 'Status', 'Effective Date', 'Contract Value', 'Governing Law', 'Created At'];
    const rows = result.rows.map((row) => [
      row.document_id,
      `"${row.file_name}"`,
      row.document_type || 'N/A',
      row.status,
      row.effective_date || 'N/A',
      `"${row.contract_value || 'N/A'}"`,
      `"${row.governing_law || 'N/A'}"`,
      new Date(row.created_at).toISOString(),
    ]);

    const csvContent = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');

    res.setHeader('Content-Type', 'text/csv');
    res.setHeader('Content-Disposition', 'attachment; filename="contract_analysis_report.csv"');
    return res.status(200).send(csvContent);
  } catch (err: any) {
    console.error('Error exporting CSV:', err);
    return res.status(500).json({ error: 'Failed to export CSV report.' });
  }
});

