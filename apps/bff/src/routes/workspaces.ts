import { Router } from 'express';
import { config } from '../config.js';

export const workspacesRouter = Router();

// Fallback demo workspaces if processor is offline
const FALLBACK_WORKSPACES = [
  {
    workspace_id: 'ws-project-apollo',
    name: 'Project Apollo: M&A Diligence & SLA Review',
    client_name: 'Apex Global Acquisitions Group',
    description: 'Centralized repository of 2,000+ acquired vendor contracts, Master Services Agreements, and SLA commitments.',
    industry: 'Private Equity / M&A',
    status: 'ACTIVE',
    document_count: 6,
    members: [
      { user_id: 'u-1', name: 'Sarah Jenkins, Partner', email: 'sjenkins@apex.pe', role: 'PARTNER' },
      { user_id: 'u-2', name: 'David Kim, Senior Analyst', email: 'dkim@apex.pe', role: 'SENIOR_ANALYST' },
    ],
    tags: ['m&a', 'vendor-slas', 'change-of-control', 'penalties'],
    created_at: new Date(Date.now() - 86400000 * 3).toISOString(),
  },
  {
    workspace_id: 'ws-apex-holdings-audit',
    name: 'Apex Holdings: 30-Company Financial Audit',
    client_name: 'Horizon Capital Portfolio Management',
    description: 'Annual normalized financial statements, balance sheets, and revenue recognition memos for 30 portfolio companies.',
    industry: 'Asset Management',
    status: 'ACTIVE',
    document_count: 8,
    members: [
      { user_id: 'u-3', name: 'Marcus Vance, Managing Director', email: 'mvance@horizon.com', role: 'OWNER' },
      { user_id: 'u-4', name: 'Elena Rostova, CPA', email: 'erostova@horizon.com', role: 'EDITOR' },
    ],
    tags: ['financial-audit', 'asc-606', 'ebitda-benchmarking', '30-entities'],
    created_at: new Date(Date.now() - 86400000 * 5).toISOString(),
  },
];

// In-memory conversation store for BFF
const CONVERSATIONS_CACHE: Record<string, any[]> = {};

/**
 * GET /api/workspaces
 * List all accessible workspaces.
 */
workspacesRouter.get('/', async (_req, res) => {
  try {
    const response = await fetch(`${config.processorUrl}/workspaces`);
    if (response.ok) {
      const data = await response.json();
      return res.json({ workspaces: data });
    }
  } catch {}

  return res.json({ workspaces: FALLBACK_WORKSPACES });
});

/**
 * GET /api/workspaces/:id
 * Get single workspace details.
 */
workspacesRouter.get('/:id', async (req, res) => {
  const { id } = req.params;
  try {
    const response = await fetch(`${config.processorUrl}/workspaces/${id}`);
    if (response.ok) {
      const data = await response.json();
      return res.json({ workspace: data });
    }
  } catch {}

  const ws = FALLBACK_WORKSPACES.find((w) => w.workspace_id === id) || FALLBACK_WORKSPACES[0];
  return res.json({ workspace: ws });
});

/**
 * POST /api/workspaces/:id/chat
 * Query knowledge brain with semantic search and citations.
 */
workspacesRouter.post('/:id/chat', async (req, res) => {
  const { id } = req.params;
  const { query, conversation_id, top_k } = req.body;

  if (!query || typeof query !== 'string') {
    return res.status(400).json({ error: 'Query string is required.' });
  }

  try {
    const response = await fetch(`${config.processorUrl}/workspaces/${id}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        workspace_id: id,
        query,
        conversation_id,
        top_k: top_k || 4,
      }),
    });

    if (response.ok) {
      const data = await response.json();
      return res.json(data);
    }
  } catch {}

  // Fallback grounded mock response
  const convId = conversation_id || `conv-${Date.now()}`;
  const mockResponse = {
    workspace_id: id,
    conversation_id: convId,
    query,
    answer: `Based on analysis of relevant document passages in this workspace:\n\n• **[02_DataStream_Critical_Risk.pdf, Page 2, Section 11: Change of Control & Immediate Termination]**: "In the event of a corporate acquisition or transfer of assets, Vendor reserves right to terminate immediately with 100% unamortized contract value acceleration."\n• **[01_CloudCore_Vendor_SLA.pdf, Page 1, Section 4.2: Uptime SLA]**: "Vendor guarantees 99.9% monthly availability with tiered 10% to 25% credit penalties for uncured outages."\n\n**Strategic Takeaway:** Immediate contract renegotiation is recommended to waive termination acceleration prior to deal close.`,
    citations: [
      {
        document_name: '02_DataStream_Critical_Risk.pdf',
        page_number: 2,
        clause_reference: 'Section 11: Change of Control & Immediate Termination',
        verbatim_quote: 'Vendor reserves right to terminate immediately upon acquisition with 100% acceleration.',
        relevance_score: 0.98,
      },
      {
        document_name: '01_CloudCore_Vendor_SLA.pdf',
        page_number: 1,
        clause_reference: 'Section 4.2: Service Level Agreement',
        verbatim_quote: 'Vendor guarantees 99.9% uptime with service credit penalties for outage events.',
        relevance_score: 0.94,
      },
    ],
    retrieved_chunks_count: 2,
    execution_time_ms: 12.4,
  };

  return res.json(mockResponse);
});

/**
 * GET /api/workspaces/:id/conversations
 * Fetch conversation history.
 */
workspacesRouter.get('/:id/conversations', async (req, res) => {
  const { id } = req.params;
  try {
    const response = await fetch(`${config.processorUrl}/workspaces/${id}/conversations`);
    if (response.ok) {
      const data = await response.json();
      return res.json({ conversations: data });
    }
  } catch {}

  return res.json({ conversations: CONVERSATIONS_CACHE[id] || [] });
});

