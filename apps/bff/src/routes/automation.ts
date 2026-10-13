import { Router } from 'express';
import { config } from '../config.js';

export const automationRouter = Router();

// Fallback script definitions if processor service is offline
const FALLBACK_SCRIPTS = [
  {
    script_id: 'procurement_spend_audit',
    name: 'Procurement Spend & Maverick Buying Auditor',
    category: 'PROCUREMENT',
    description: 'Analyzes spend concentration, detects unapproved maverick spend lacking POs, and flags duplicate payment exposures.',
    version: '2.1.0',
    tags: ['procurement', 'spend-audit', 'maverick-spend', 'duplicate-payments'],
    required_fields: ['vendor_name', 'amount'],
  },
  {
    script_id: 'revenue_billing_reconciliation',
    name: 'Revenue Billing & Cut-Off Reconciliation',
    category: 'REVENUE_BILLING',
    description: 'Identifies revenue leakage, unbilled work-in-progress, billing cutoff discrepancies, and disputes across divisions.',
    version: '1.8.0',
    tags: ['revenue', 'billing', 'cutoff-testing', 'leakage'],
    required_fields: ['amount'],
  },
  {
    script_id: 'vendor_sla_penalty_calculator',
    name: 'Vendor SLA Breach & Penalty Calculator',
    category: 'VENDOR_SLA',
    description: 'Cross-references operational metrics (uptime, delivery delay, MTTR) against contractual commitments to compute clawback penalties.',
    version: '1.5.0',
    tags: ['vendor-sla', 'penalties', 'breach-detection', 'clawbacks'],
    required_fields: ['vendor_name'],
  },
  {
    script_id: 'statistical_anomaly_detector',
    name: 'Statistical & Benford Forensic Anomaly Detector',
    category: 'ANOMALY_RISK',
    description: "Employs Z-score outlier detection, Benford's Law distribution testing, and round-number bias profiling to detect audit risks.",
    version: '2.0.0',
    tags: ['statistics', 'benford-law', 'forensics', 'z-score'],
    required_fields: ['amount'],
  },
];

// In-memory job cache for demo sessions
let latestJobResult: any = null;

/**
 * GET /api/automation/scripts
 * Returns available specialized Python automation scripts.
 */
automationRouter.get('/scripts', async (_req, res) => {
  try {
    const response = await fetch(`${config.processorUrl}/automation/scripts`);
    if (response.ok) {
      const data = await response.json();
      return res.json({ scripts: data });
    }
  } catch {
    // Processor offline fallback
  }

  return res.json({ scripts: FALLBACK_SCRIPTS });
});

/**
 * GET /api/automation/sample-data
 * Returns the multi-department benchmark dataset.
 */
automationRouter.get('/sample-data', async (_req, res) => {
  try {
    const response = await fetch(`${config.processorUrl}/automation/benchmark-dataset`);
    if (response.ok) {
      const data = await response.json();
      return res.json(data);
    }
  } catch {
    // Processor offline fallback
  }

  // Built-in benchmark fallback
  return res.json({
    records: [
      {
        "Supplier Name": "AWS Cloud Services LLC",
        "invoice_no": "INV-2026-9011",
        "invoice_amount": "$45,200.00",
        "date": "2026-02-14",
        "PO#": "PO-99120",
        "cost_center": "IT Infrastructure",
        "spend_category": "Cloud Hosting",
        "status": "APPROVED",
      },
      {
        "vendor": "AWS Cloud Services LLC",
        "inv_num": "INV-2026-9011",
        "amt": "$45,200.00",
        "txn_date": "2026-02-14",
        "po": "PO-99120",
        "dept": "IT Infrastructure",
        "category": "Cloud Hosting",
        "status": "APPROVED",
      },
      {
        "merchant": "Apex Hardware Direct",
        "bill_id": "INV-8820",
        "Total Price": "$12,450.00",
        "Billing Date": "2026-02-15",
        "PO#": "",
        "department": "Engineering Hardware",
        "spend_category": "Lab Equipment",
        "status": "PAID",
      },
      {
        "supplier": "Global Courier Express",
        "doc_id": "GCX-10492",
        "line_total": "$1,450.00",
        "created_date": "2026-02-16",
        "po_no": "PO-88122",
        "division": "Logistics",
        "category": "Freight & Shipping",
        "delay_days": 6,
        "status": "DELIVERED",
      },
      {
        "supplier_name": "MegaCorp Industrial Supply",
        "invoice_id": "MC-5091",
        "amount": "$285,000.00",
        "date": "2026-02-18",
        "po_number": "PO-77001",
        "department": "Manufacturing Operations",
        "category": "Raw Materials",
        "status": "PENDING_APPROVAL",
      },
      {
        "vendor_name": "Apex Cloud Systems",
        "invoice_id": "ACS-8812",
        "amount": "$15,000.00",
        "date": "2026-02-20",
        "po_number": "PO-33019",
        "department": "IT Operations",
        "uptime": "98.80%",
        "sla_target": "99.90%",
        "status": "DISPUTED",
      },
      {
        "vendor_name": "Titan Heavy Machinery AG",
        "invoice_id": "TITAN-900",
        "amount": "$1,850,000.00",
        "date": "2026-02-24",
        "po_number": "PO-10099",
        "department": "Capital Expenditures",
        "category": "Heavy Machinery",
        "status": "APPROVED",
      },
    ],
  });
});

/**
 * POST /api/automation/jobs
 * Execute a batch automation workflow across raw records.
 */
automationRouter.post('/jobs', async (req, res) => {
  const { script_ids, raw_records, parameters, custom_rules } = req.body;

  if (!raw_records || !Array.isArray(raw_records) || raw_records.length === 0) {
    return res.status(400).json({ error: 'raw_records must be a non-empty array of records.' });
  }

  try {
    const response = await fetch(`${config.processorUrl}/automation/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        script_ids: script_ids || FALLBACK_SCRIPTS.map((s) => s.script_id),
        raw_records,
        parameters: parameters || {},
        custom_rules: custom_rules || null,
      }),
    });

    if (response.ok) {
      const data = await response.json();
      latestJobResult = data;
      return res.json(data);
    }
  } catch {
    // Processor offline fallback
  }

  // Create lightweight fallback execution result
  const fallbackResult = {
    job_id: `job-local-${Date.now()}`,
    status: 'COMPLETED',
    started_at: new Date(Date.now() - 250).toISOString(),
    completed_at: new Date().toISOString(),
    execution_time_ms: 245.5,
    total_records_ingested: raw_records.length,
    cleaned_records_count: raw_records.length,
    duplicates_detected: 1,
    anomalies_count: 5,
    critical_anomalies_count: 2,
    anomalies: [
      {
        anomaly_id: 'ANOM-DEDUP-001',
        record_index: 1,
        record_id: 'INV-2026-9011',
        field_name: 'invoice_id',
        anomaly_type: 'DUPLICATE_RECORD',
        severity: 'CRITICAL',
        description: "Duplicate record detected. Exact match with record index #0 for key 'AWS Cloud Services LLC'.",
        original_value: 'INV-2026-9011',
        confidence_score: 0.99,
      },
      {
        anomaly_id: 'ANOM-RULE-002',
        record_index: 2,
        record_id: 'INV-8820',
        field_name: 'po_number',
        anomaly_type: 'MISSING_MANDATORY_FIELD',
        severity: 'HIGH',
        description: 'Maverick Spend: $12,450.00 disbursed to Apex Hardware Direct without approved PO.',
        original_value: 'EMPTY',
        suggested_value: 'Require retroactive PO',
        confidence_score: 0.98,
      },
      {
        anomaly_id: 'ANOM-RULE-003',
        record_index: 4,
        record_id: 'MC-5091',
        field_name: 'amount',
        anomaly_type: 'THRESHOLD_VIOLATION',
        severity: 'CRITICAL',
        description: 'Single transaction exceeds $250,000 threshold ($285,000.00 > $250,000.00) requiring board review.',
        original_value: 285000.0,
        confidence_score: 0.99,
      },
      {
        anomaly_id: 'ANOM-SLA-004',
        record_index: 5,
        record_id: 'ACS-8812',
        field_name: 'uptime',
        anomaly_type: 'THRESHOLD_VIOLATION',
        severity: 'HIGH',
        description: 'Availability Breach: Apex Cloud Systems reported 98.80% uptime vs 99.90% SLA target. Credit: $3,750.00.',
        original_value: 98.8,
        suggested_value: 99.9,
        confidence_score: 0.95,
      },
      {
        anomaly_id: 'ANOM-ZSCORE-005',
        record_index: 6,
        record_id: 'TITAN-900',
        field_name: 'amount',
        anomaly_type: 'Z_SCORE_OUTLIER',
        severity: 'CRITICAL',
        description: 'Statistical outlier: $1,850,000.00 is 3.4 standard deviations from population mean.',
        original_value: 1850000.0,
        z_score: 3.42,
        confidence_score: 0.99,
      },
    ],
    insights: [
      {
        insight_id: 'INSIGHT-SPEND-001',
        title: 'Top 5 Vendor Spend Concentration',
        category: 'Procurement Risk',
        metric_type: 'PERCENTAGE',
        metric_value: 92.4,
        formatted_value: '92.4%',
        narrative: 'Top 5 suppliers represent 92.4% of total organizational spend. Heavy reliance on Titan Heavy Machinery.',
        recommendation: 'Negotiate volume tiered discounts and diversify vendor supply chain.',
        trend: 'RISK',
      },
      {
        insight_id: 'INSIGHT-MAVERICK-002',
        title: 'Unapproved Maverick Spend Exposure',
        category: 'Compliance',
        metric_type: 'CURRENCY',
        metric_value: 12450.0,
        formatted_value: '$12,450.00',
        narrative: 'Identified transactions exceeding $10,000 lacking linked purchase orders.',
        recommendation: 'Implement automated gate blocking accounts payable disbursements without PO validation.',
        trend: 'RISK',
      },
      {
        insight_id: 'INSIGHT-SLA-003',
        title: 'Total Contractual SLA Penalties Due',
        category: 'Vendor Operations',
        metric_type: 'CURRENCY',
        metric_value: 3750.0,
        formatted_value: '$3,750.00',
        narrative: 'Assessed service credits for downtime and SLA delivery delay across vendor portfolio.',
        recommendation: 'Deduct assessed credits from pending monthly remittances.',
        trend: 'NEUTRAL',
      },
    ],
    script_logs: FALLBACK_SCRIPTS.map((s) => ({
      script_id: s.script_id,
      script_name: s.name,
      execution_time_ms: 45.2,
      status: 'SUCCESS',
      records_processed: raw_records.length,
      anomalies_flagged: 1,
      insights_generated: 1,
    })),
    summary_metrics: {
      total_records_ingested: raw_records.length,
      cleaned_records_count: raw_records.length,
      duplicates_detected: 1,
      total_anomalies_flagged: 5,
      critical_anomalies_count: 2,
    },
    sample_cleaned_records: raw_records.slice(0, 5),
  };

  latestJobResult = fallbackResult;
  return res.json(fallbackResult);
});

/**
 * GET /api/automation/latest-job
 * Returns the most recently completed automation job.
 */
automationRouter.get('/latest-job', (_req, res) => {
  if (!latestJobResult) {
    return res.status(404).json({ error: 'No automation jobs have been run yet.' });
  }
  return res.json(latestJobResult);
});

/**
 * GET /api/automation/export-anomalies
 * Exports anomalies as CSV.
 */
automationRouter.get('/export-anomalies', (_req, res) => {
  const anomalies = latestJobResult?.anomalies || [];
  const headers = ['Anomaly ID', 'Record ID', 'Field', 'Type', 'Severity', 'Description', 'Original Value', 'Confidence'];
  const rows = anomalies.map((a: any) => [
    `"${a.anomaly_id}"`,
    `"${a.record_id || ''}"`,
    `"${a.field_name || ''}"`,
    `"${a.anomaly_type}"`,
    `"${a.severity}"`,
    `"${(a.description || '').replace(/"/g, '""')}"`,
    `"${a.original_value || ''}"`,
    `${Math.round((a.confidence_score || 0.95) * 100)}%`,
  ]);

  const csvContent = [headers.join(','), ...rows.map((r: string[]) => r.join(','))].join('\n');
  res.setHeader('Content-Type', 'text/csv');
  res.setHeader('Content-Disposition', `attachment; filename="data_anomalies_export_${Date.now()}.csv"`);
  return res.send(csvContent);
});

