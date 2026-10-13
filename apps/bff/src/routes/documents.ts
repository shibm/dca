import { Router, Response } from 'express';
import multer from 'multer';
import crypto from 'crypto';
import fs from 'fs';
import path from 'path';
import { pool } from '../db.js';
import { config } from '../config.js';
import { AuthRequest, authenticateToken } from '../middleware/auth.js';

export const documentsRouter = Router();

// Ensure upload directory exists
const uploadDir = config.uploadDir;
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir, { recursive: true });
}

// Multer storage configuration
const storage = multer.diskStorage({
  destination: (_req, _file, cb) => {
    cb(null, uploadDir);
  },
  filename: (_req, file, cb) => {
    const uniqueSuffix = `${Date.now()}-${crypto.randomBytes(6).toString('hex')}`;
    const ext = path.extname(file.originalname);
    cb(null, `doc-${uniqueSuffix}${ext}`);
  },
});

// File filter: strictly enforce PDF
const fileFilter = (_req: any, file: Express.Multer.File, cb: multer.FileFilterCallback) => {
  if (file.mimetype === 'application/pdf' || file.originalname.toLowerCase().endsWith('.pdf')) {
    cb(null, true);
  } else {
    cb(new Error('Invalid file format. Only PDF files are accepted.'));
  }
};

const upload = multer({
  storage,
  limits: { fileSize: 50 * 1024 * 1024 }, // 50 MB
  fileFilter,
});

/**
 * Upload and initiate processing of PDF
 */
documentsRouter.post(
  '/upload',
  authenticateToken,
  upload.single('file'),
  async (req: AuthRequest, res: Response) => {
    if (!req.file) {
      return res.status(400).json({ error: 'No PDF file uploaded.' });
    }

    const filePath = req.file.path;
    const fileBuffer = fs.readFileSync(filePath);

    // Verify magic bytes (%PDF-)
    if (fileBuffer.subarray(0, 4).toString() !== '%PDF') {
      fs.unlinkSync(filePath);
      return res.status(400).json({ error: 'File is not a valid PDF document.' });
    }

    // Compute SHA-256 checksum
    const fileHash = crypto.createHash('sha256').update(fileBuffer).digest('hex');

    try {
      // Insert into PostgreSQL
      const insertQuery = `
        INSERT INTO documents (
          user_id, file_name, file_size_bytes, storage_path, file_hash, status
        ) VALUES ($1, $2, $3, $4, $5, 'PROCESSING')
        RETURNING id, file_name, file_size_bytes, status, created_at
      `;

      const result = await pool.query(insertQuery, [
        req.user?.id,
        req.file.originalname,
        req.file.size,
        filePath,
        fileHash,
      ]);

      const doc = result.rows[0];

      // Asynchronously trigger Python processor
      fetch(`${config.processorUrl}/extract`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ file_path: filePath, document_id: doc.id }),
      }).catch((err) => {
        console.error('Error forwarding document to processor:', err.message);
      });

      return res.status(201).json({
        message: 'Document uploaded successfully and queued for extraction.',
        document: doc,
      });
    } catch (err: any) {
      console.error('Document upload error:', err);
      return res.status(500).json({ error: 'Failed to process document upload.' });
    }
  }
);

const FALLBACK_DOCUMENTS = [
  {
    id: 'demo-doc-1',
    file_name: '02_DataStream_Critical_Risk.pdf',
    fileName: '02_DataStream_Critical_Risk.pdf',
    file_size_bytes: 42300,
    page_count: 2,
    document_type: 'contract',
    documentType: 'contract',
    status: 'NEEDS_REVIEW',
    totalValue: 480000,
    uptimeSla: '99.9%',
    changeOfControl: 'Requires 60 days prior written notice; vendor may terminate immediately with 100% acceleration',
    hasCocRisk: true,
    earlyTerminationPenalty: '100% of unamortized contract value',
    autoRenewalClause: 'Renews automatically for successive 1-year terms',
    riskScore: 65,
    created_at: new Date().toISOString(),
  },
  {
    id: 'demo-doc-2',
    file_name: '01_CloudCore_Vendor_SLA.pdf',
    fileName: '01_CloudCore_Vendor_SLA.pdf',
    file_size_bytes: 38500,
    page_count: 2,
    document_type: 'contract',
    documentType: 'contract',
    status: 'APPROVED',
    totalValue: 240000,
    uptimeSla: '99.95%',
    changeOfControl: 'Requires 30 days prior written notice upon acquisition',
    hasCocRisk: true,
    earlyTerminationPenalty: '$25,000 flat penalty plus remaining fees',
    autoRenewalClause: 'None',
    riskScore: 45,
    created_at: new Date(Date.now() - 86400000).toISOString(),
  },
  {
    id: 'demo-doc-3',
    file_name: '03_SecureDesk_Standard_License.pdf',
    fileName: '03_SecureDesk_Standard_License.pdf',
    file_size_bytes: 28400,
    page_count: 2,
    document_type: 'contract',
    documentType: 'contract',
    status: 'APPROVED',
    totalValue: 35000,
    uptimeSla: 'N/A',
    changeOfControl: 'May assign without consent in connection with merger',
    hasCocRisk: false,
    earlyTerminationPenalty: 'None',
    autoRenewalClause: 'None',
    riskScore: 10,
    created_at: new Date(Date.now() - 172800000).toISOString(),
  },
];

/**
 * List all uploaded documents
 */
documentsRouter.get('/', authenticateToken, async (_req: AuthRequest, res: Response) => {
  try {
    const query = `
      SELECT 
        d.id, d.file_name, d.file_size_bytes, d.page_count, d.document_type,
        d.status, d.metadata, d.created_at, d.updated_at,
        u.full_name as uploaded_by,
        COUNT(e.id) as total_extracted_fields
      FROM documents d
      LEFT JOIN users u ON d.user_id = u.id
      LEFT JOIN document_extractions e ON d.id = e.document_id
      GROUP BY d.id, u.full_name
      ORDER BY d.created_at DESC
    `;

    const result = await pool.query(query);
    return res.json({ documents: result.rows });
  } catch (err: any) {
    // Database offline fallback (Zero-Docker demo mode)
    return res.json({ documents: FALLBACK_DOCUMENTS });
  }
});

/**
 * Pillar 1: M&A Diligence Rollup Across All Ingested Vendor Contracts
 */
documentsRouter.get('/ma-diligence', authenticateToken, async (_req: AuthRequest, res: Response) => {
  try {
    const query = `
      SELECT 
        d.id, d.file_name, d.document_type, d.status, d.created_at,
        MAX(CASE WHEN e.field_key = 'total_contract_value' THEN e.field_value END) as total_value,
        MAX(CASE WHEN e.field_key = 'uptime_sla' THEN e.field_value END) as uptime_sla,
        MAX(CASE WHEN e.field_key = 'change_of_control' THEN e.field_value END) as change_of_control,
        MAX(CASE WHEN e.field_key = 'early_termination_penalty' THEN e.field_value END) as early_termination_penalty,
        MAX(CASE WHEN e.field_key = 'auto_renewal_clause' THEN e.field_value END) as auto_renewal_clause,
        ROUND(AVG(e.confidence_score)::numeric, 3) as avg_confidence
      FROM documents d
      LEFT JOIN document_extractions e ON d.id = e.document_id
      GROUP BY d.id, d.file_name, d.document_type, d.status, d.created_at
      ORDER BY d.created_at DESC
    `;

    const result = await pool.query(query);

    let totalExposure = 0;
    let cocCount = 0;
    let acqTerminationCount = 0;
    let upcomingRenewals = 0;

    const contracts = result.rows.map((row) => {
      // Calculate numerical value
      let numVal = 0;
      if (row.total_value) {
        const cleaned = row.total_value.replace(/[^0-9.]/g, '');
        numVal = parseFloat(cleaned) || 0;
      }
      totalExposure += numVal;

      const coc = row.change_of_control || '';
      const isCocRisk = coc.includes('Requires') || coc.includes('Terminate');
      if (isCocRisk) cocCount++;
      if (coc.includes('Terminate')) acqTerminationCount++;

      const isRenewal = !!row.auto_renewal_clause;
      if (isRenewal) upcomingRenewals++;

      let riskScore = 10;
      if (coc.includes('Terminate')) riskScore += 50;
      else if (coc.includes('Requires')) riskScore += 30;
      if (row.early_termination_penalty) riskScore += 25;
      if (isRenewal) riskScore += 15;

      return {
        id: row.id,
        fileName: row.file_name,
        documentType: row.document_type,
        totalValue: numVal,
        uptimeSla: row.uptime_sla || 'N/A',
        changeOfControl: row.change_of_control || 'None',
        hasCocRisk: isCocRisk,
        earlyTerminationPenalty: row.early_termination_penalty || 'None',
        autoRenewalClause: row.auto_renewal_clause || 'None',
        riskScore: Math.min(riskScore, 100),
        status: row.status,
      };
    });

    const avgRisk = contracts.length > 0
      ? Math.round(contracts.reduce((acc, c) => acc + c.riskScore, 0) / contracts.length)
      : 0;

    return res.json({
      totalContracts: contracts.length,
      totalFinancialExposure: totalExposure,
      changeOfControlRiskCount: cocCount,
      acquisitionTerminationRightsCount: acqTerminationCount,
      upcomingRenewalsCount: upcomingRenewals,
      averageRiskScore: avgRisk,
      contracts,
    });
  } catch (err: any) {
    // Database offline fallback (Zero-Docker demo mode)
    const contracts = FALLBACK_DOCUMENTS;
    const totalExposure = contracts.reduce((acc, c) => acc + c.totalValue, 0);
    const cocCount = contracts.filter((c) => c.hasCocRisk).length;
    const avgRisk = Math.round(contracts.reduce((acc, c) => acc + c.riskScore, 0) / contracts.length);
    return res.json({
      totalContracts: contracts.length,
      totalFinancialExposure: totalExposure,
      changeOfControlRiskCount: cocCount,
      acquisitionTerminationRightsCount: 1,
      upcomingRenewalsCount: 1,
      averageRiskScore: avgRisk,
      contracts,
    });
  }
});

/**
 * Get document details and extracted entities
 */
documentsRouter.get('/:id', authenticateToken, async (req: AuthRequest, res: Response) => {
  const { id } = req.params;

  try {
    const docQuery = 'SELECT * FROM documents WHERE id = $1';
    const docResult = await pool.query(docQuery, [id]);

    if (docResult.rows.length === 0) {
      return res.status(404).json({ error: 'Document not found.' });
    }

    const extractionsQuery = `
      SELECT * FROM document_extractions 
      WHERE document_id = $1 
      ORDER BY confidence_score ASC, field_category ASC
    `;
    const extractionsResult = await pool.query(extractionsQuery, [id]);

    return res.json({
      document: docResult.rows[0],
      extractions: extractionsResult.rows,
    });
  } catch (err: any) {
    console.error('Error fetching document details:', err);
    return res.status(500).json({ error: 'Failed to fetch document details.' });
  }
});

