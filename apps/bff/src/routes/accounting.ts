import { Router, Response } from 'express';
import { AuthRequest, authenticateToken } from '../middleware/auth.js';
import { config } from '../config.js';

export const accountingRouter = Router();

// In-memory demo store for accounting memos (allows immediate interactive review & edit)
let MEMOS_STORE: Record<string, any> = {
  'demo-memo-1': {
    memoId: 'MEMO-ASC606-B83C992C',
    contractTitle: 'Master Services Agreement & SaaS Subscription',
    parties: ['Acme Global Technologies Inc.', 'Apex Cloud Solutions LLC'],
    contractValue: 175000.0,
    currency: 'USD',
    effectiveDate: 'October 15, 2026',
    accountingStandard: 'ASC_606_REVENUE',
    status: 'DRAFT',
    executiveSummary:
      'Technical accounting evaluation for Master Services Agreement between Acme Global Technologies Inc. and Apex Cloud Solutions LLC. Under ASC 606, the arrangement contains 2 distinct performance obligations. Total transaction price of $175,000.00 USD is allocated and recognized over time for SaaS access and at a point in time for professional services.',
    asc606Analysis: {
      step1Assessment:
        'The contract meets all criteria in ASC 606-10-25-1: enforceable rights, commercial substance, defined Net 30 payment terms, and probable collectibility.',
      step2PerformanceObligations: [
        {
          id: 'PPOB-1',
          name: 'Cloud SaaS Subscription Platform Access',
          distinctInContext: true,
          standaloneSellingPrice: 140000.0,
          allocatedTransactionPrice: 140000.0,
          timingOfSatisfaction: 'OVER_TIME',
          recognitionPeriod: 'Ratable monthly over 12-month term',
          contractCitation: 'Customer receives continuous hosted access to the proprietary platform.',
        },
        {
          id: 'PPOB-2',
          name: 'Implementation & Technical Onboarding Services',
          distinctInContext: true,
          standaloneSellingPrice: 35000.0,
          allocatedTransactionPrice: 35000.0,
          timingOfSatisfaction: 'POINT_IN_TIME',
          recognitionPeriod: 'Recognized upon milestone completion and formal acceptance',
          contractCitation: 'Provider shall deliver initial cloud migration and environment onboarding.',
        },
      ],
      step2Assessment:
        'SaaS platform access and implementation services are capable of being distinct and distinct within the context of the agreement.',
      step3TotalTransactionPrice: 175000.0,
      step3Assessment:
        'Total fixed consideration is $175,000.00 USD. No variable consideration estimates or significant financing components.',
      step4Assessment:
        'Allocated based on relative Standalone Selling Price (SSP): SaaS Access 80% ($140,000.00) and Implementation Services 20% ($35,000.00).',
      step5RecognitionSummary:
        'SaaS access recognized straight-line over 12 months ($11,666.67/month). Implementation recognized point-in-time upon milestone sign-off.',
    },
    suggestedJournalEntries: [
      {
        scheduleId: 'JE-001',
        eventName: 'Initial Invoicing on Contract Effective Date',
        period: 'October 15, 2026',
        totalDebit: 175000.0,
        totalCredit: 175000.0,
        isBalanced: true,
        lines: [
          {
            accountNumber: '1100',
            accountName: 'Accounts Receivable',
            debit: 175000.0,
            credit: null,
            description: 'To record initial contract billing at effective date',
          },
          {
            accountNumber: '2200',
            accountName: 'Deferred Revenue – SaaS Subscription',
            debit: null,
            credit: 140000.0,
            description: 'To record unearned SaaS subscription revenue',
          },
          {
            accountNumber: '2250',
            accountName: 'Deferred Revenue – Professional Services',
            debit: null,
            credit: 35000.0,
            description: 'To record unearned implementation service fee',
          },
        ],
      },
      {
        scheduleId: 'JE-002',
        eventName: 'Monthly Subscription Revenue Amortization (Recurring 12 Months)',
        period: 'Monthly Periods 1 through 12',
        totalDebit: 11666.67,
        totalCredit: 11666.67,
        isBalanced: true,
        lines: [
          {
            accountNumber: '2200',
            accountName: 'Deferred Revenue – SaaS Subscription',
            debit: 11666.67,
            credit: null,
            description: 'Monthly amortization of deferred SaaS subscription',
          },
          {
            accountNumber: '4100',
            accountName: 'SaaS Subscription Revenue',
            debit: null,
            credit: 11666.67,
            description: 'Ratable monthly revenue recognition under ASC 606',
          },
        ],
      },
      {
        scheduleId: 'JE-003',
        eventName: 'Implementation Services Milestone Completion',
        period: 'Upon Milestone Acceptance (~Day 60)',
        totalDebit: 35000.0,
        totalCredit: 35000.0,
        isBalanced: true,
        lines: [
          {
            accountNumber: '2250',
            accountName: 'Deferred Revenue – Professional Services',
            debit: 35000.0,
            credit: null,
            description: 'Release deferred revenue upon customer milestone sign-off',
          },
          {
            accountNumber: '4200',
            accountName: 'Professional Services Revenue',
            debit: null,
            credit: 35000.0,
            description: 'Point-in-time revenue recognition upon environment acceptance',
          },
        ],
      },
    ],
    conclusionAndDisclosures:
      'CONCLUSION: The contract meets all criteria for recognition under ASC 606. Management will record an initial debit to Accounts Receivable and credit to Deferred Revenue of $175,000.00. Deferred revenue will be amortized to SaaS Subscription Revenue straight-line at $11,666.67/month. Disclosures required under ASC 606-10-50 regarding remaining performance obligations (RPO) must be included in quarterly filings.',
  },
};

/**
 * List all generated technical accounting memos
 */
accountingRouter.get('/memos', authenticateToken, async (_req: AuthRequest, res: Response) => {
  return res.json({ memos: Object.values(MEMOS_STORE) });
});

/**
 * Get single technical accounting memo by ID
 */
accountingRouter.get('/memos/:id', authenticateToken, async (req: AuthRequest, res: Response) => {
  const memo = MEMOS_STORE[req.params.id] || MEMOS_STORE['demo-memo-1'];
  if (!memo) return res.status(404).json({ error: 'Memo not found.' });
  return res.json({ memo });
});

/**
 * Expert Reviewer Edit: Update memo notes or journal entries
 */
accountingRouter.patch('/memos/:id', authenticateToken, async (req: AuthRequest, res: Response) => {
  const memo = MEMOS_STORE[req.params.id] || MEMOS_STORE['demo-memo-1'];
  if (!memo) return res.status(404).json({ error: 'Memo not found.' });

  const { executiveSummary, conclusionAndDisclosures, suggestedJournalEntries } = req.body;
  if (executiveSummary !== undefined) memo.executiveSummary = executiveSummary;
  if (conclusionAndDisclosures !== undefined) memo.conclusionAndDisclosures = conclusionAndDisclosures;
  if (suggestedJournalEntries !== undefined) memo.suggestedJournalEntries = suggestedJournalEntries;

  return res.json({ message: 'Accounting memo updated successfully.', memo });
});

/**
 * Approve & Finalize Technical Accounting Memo
 */
accountingRouter.post('/memos/:id/approve', authenticateToken, async (req: AuthRequest, res: Response) => {
  const memo = MEMOS_STORE[req.params.id] || MEMOS_STORE['demo-memo-1'];
  if (!memo) return res.status(404).json({ error: 'Memo not found.' });

  memo.status = 'APPROVED';
  memo.reviewedBy = req.user?.email || 'Senior Technical Accounting Reviewer';

  return res.json({ message: 'Technical accounting memo approved.', memo });
});

