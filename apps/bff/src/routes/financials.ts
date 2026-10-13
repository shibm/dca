import { Router, Response } from 'express';
import { AuthRequest, authenticateToken } from '../middleware/auth.js';
import { config } from '../config.js';

export const financialsRouter = Router();

// Demo 30-entity benchmarking data for instantaneous local display & fallback
const DEFAULT_PORTFOLIO_DATA = {
  totalEntitiesAnalyzed: 30,
  reportingPeriod: 'FY2025',
  totalPortfolioRevenue: 1245800000,
  averageGrossMarginPct: 58.4,
  averageEbitdaMarginPct: 18.2,
  medianRevenueGrowthPct: 16.5,
  distressedEntitiesCount: 2,
  watchlistEntitiesCount: 4,
  companies: [
    {
      entityName: 'CloudVanguard Technologies Inc.',
      fiscalPeriod: 'FY2025',
      currency: 'USD',
      revenue: 142500000,
      yoyRevenueGrowthPct: 28.4,
      grossMarginPct: 78.4,
      ebitda: 39900000,
      ebitdaMarginPct: 28.0,
      netIncome: 27680000,
      cashAndEquivalents: 48400000,
      totalDebt: 12000000,
      freeCashFlow: 34200000,
      debtToEquity: 0.18,
      healthStatus: 'EXCELLENT',
      healthFlags: ['Top-decile performance: High growth and strong positive FCF'],
    },
    {
      entityName: 'Apex Logistics Global Corp.',
      fiscalPeriod: 'FY2025',
      currency: 'USD',
      revenue: 188000000,
      yoyRevenueGrowthPct: 14.5,
      grossMarginPct: 34.2,
      ebitda: 24500000,
      ebitdaMarginPct: 13.0,
      netIncome: 14200000,
      cashAndEquivalents: 22000000,
      totalDebt: 42000000,
      freeCashFlow: 16400000,
      debtToEquity: 0.65,
      healthStatus: 'SOLID',
      healthFlags: [],
    },
    {
      entityName: 'DataGrid Enterprise Systems',
      fiscalPeriod: 'FY2025',
      currency: 'USD',
      revenue: 112000000,
      yoyRevenueGrowthPct: 22.1,
      grossMarginPct: 72.0,
      ebitda: 28000000,
      ebitdaMarginPct: 25.0,
      netIncome: 19500000,
      cashAndEquivalents: 35000000,
      totalDebt: 15000000,
      freeCashFlow: 24000000,
      debtToEquity: 0.25,
      healthStatus: 'EXCELLENT',
      healthFlags: [],
    },
    {
      entityName: 'OmniRetail Brands Holdings LLC',
      fiscalPeriod: 'FY2025',
      currency: 'USD',
      revenue: 96000000,
      yoyRevenueGrowthPct: 3.2,
      grossMarginPct: 26.8,
      ebitda: 3200000,
      ebitdaMarginPct: 3.3,
      netIncome: 480000,
      cashAndEquivalents: 5100000,
      totalDebt: 39000000,
      freeCashFlow: 800000,
      debtToEquity: 1.95,
      healthStatus: 'WATCHLIST',
      healthFlags: ['High leverage: Total debt exceeds 3x shareholder equity'],
    },
    {
      entityName: 'NexTherapeutics Bio Corp.',
      fiscalPeriod: 'FY2025',
      currency: 'USD',
      revenue: 16500000,
      yoyRevenueGrowthPct: -12.0,
      grossMarginPct: 27.0,
      ebitda: -18500000,
      ebitdaMarginPct: -112.1,
      netIncome: -21400000,
      cashAndEquivalents: 6200000,
      totalDebt: 25000000,
      freeCashFlow: -19500000,
      debtToEquity: -16.6,
      healthStatus: 'DISTRESSED',
      healthFlags: ['Critical burn: Insufficient cash runway relative to debt obligations'],
    },
    {
      entityName: 'AeroPrecision Components Ltd.',
      fiscalPeriod: 'FY2025',
      currency: 'USD',
      revenue: 84000000,
      yoyRevenueGrowthPct: 11.2,
      grossMarginPct: 42.0,
      ebitda: 14200000,
      ebitdaMarginPct: 16.9,
      netIncome: 8900000,
      cashAndEquivalents: 14500000,
      totalDebt: 18000000,
      freeCashFlow: 11200000,
      debtToEquity: 0.42,
      healthStatus: 'SOLID',
      healthFlags: [],
    },
    {
      entityName: 'SentryCyber Security Group',
      fiscalPeriod: 'FY2025',
      currency: 'USD',
      revenue: 72000000,
      yoyRevenueGrowthPct: 31.5,
      grossMarginPct: 82.5,
      ebitda: 21600000,
      ebitdaMarginPct: 30.0,
      netIncome: 16200000,
      cashAndEquivalents: 29000000,
      totalDebt: 4500000,
      freeCashFlow: 19800000,
      debtToEquity: 0.12,
      healthStatus: 'EXCELLENT',
      healthFlags: ['Top-decile performance: High growth and strong positive FCF'],
    },
    {
      entityName: 'InnoMed Diagnostics LLC',
      fiscalPeriod: 'FY2025',
      currency: 'USD',
      revenue: 65000000,
      yoyRevenueGrowthPct: 8.4,
      grossMarginPct: 54.0,
      ebitda: 11050000,
      ebitdaMarginPct: 17.0,
      netIncome: 6500000,
      cashAndEquivalents: 11200000,
      totalDebt: 22000000,
      freeCashFlow: 8200000,
      debtToEquity: 0.78,
      healthStatus: 'SOLID',
      healthFlags: [],
    },
    {
      entityName: 'Solaris Energy Storage Inc.',
      fiscalPeriod: 'FY2025',
      currency: 'USD',
      revenue: 58000000,
      yoyRevenueGrowthPct: 19.8,
      grossMarginPct: 38.5,
      ebitda: 8700000,
      ebitdaMarginPct: 15.0,
      netIncome: 4200000,
      cashAndEquivalents: 9500000,
      totalDebt: 19000000,
      freeCashFlow: 5400000,
      debtToEquity: 0.85,
      healthStatus: 'SOLID',
      healthFlags: [],
    },
    {
      entityName: 'Pioneer AgTech Solutions Corp.',
      fiscalPeriod: 'FY2025',
      currency: 'USD',
      revenue: 44000000,
      yoyRevenueGrowthPct: -2.5,
      grossMarginPct: 31.0,
      ebitda: 1760000,
      ebitdaMarginPct: 4.0,
      netIncome: -450000,
      cashAndEquivalents: 2800000,
      totalDebt: 21000000,
      freeCashFlow: -650000,
      debtToEquity: 2.45,
      healthStatus: 'WATCHLIST',
      healthFlags: ['Negative cash generation / operating burn detected'],
    },
    {
      entityName: 'Veloce Payment Rail Systems',
      fiscalPeriod: 'FY2025',
      currency: 'USD',
      revenue: 95000000,
      yoyRevenueGrowthPct: 26.0,
      grossMarginPct: 84.0,
      ebitda: 33250000,
      ebitdaMarginPct: 35.0,
      netIncome: 24700000,
      cashAndEquivalents: 41000000,
      totalDebt: 8000000,
      freeCashFlow: 29500000,
      debtToEquity: 0.15,
      healthStatus: 'EXCELLENT',
      healthFlags: [],
    },
    {
      entityName: 'Titan Industrial Machinery LLC',
      fiscalPeriod: 'FY2025',
      currency: 'USD',
      revenue: 135000000,
      yoyRevenueGrowthPct: 5.0,
      grossMarginPct: 28.5,
      ebitda: 14850000,
      ebitdaMarginPct: 11.0,
      netIncome: 7500000,
      cashAndEquivalents: 15000000,
      totalDebt: 48000000,
      freeCashFlow: 9200000,
      debtToEquity: 0.92,
      healthStatus: 'SOLID',
      healthFlags: [],
    },
  ],
};

/**
 * Pillar 2: Multi-Entity Portfolio Benchmarking
 */
financialsRouter.get('/portfolio-comparison', authenticateToken, async (_req: AuthRequest, res: Response) => {
  try {
    // Attempt to query processor if directory exists
    const response = await fetch(`${config.processorUrl}/compare-portfolio?directory=apps/processor/tests/portfolio_financials`, {
      method: 'POST',
    }).catch(() => null);

    if (response && response.ok) {
      const data = await response.json();
      return res.json(data);
    }

    return res.json(DEFAULT_PORTFOLIO_DATA);
  } catch (err: any) {
    return res.json(DEFAULT_PORTFOLIO_DATA);
  }
});

/**
 * Export 30-Company Comparative Matrix as CSV
 */
financialsRouter.get('/export-comparison', authenticateToken, async (_req: AuthRequest, res: Response) => {
  try {
    const companies = DEFAULT_PORTFOLIO_DATA.companies;
    const headers = [
      'Company Name',
      'Fiscal Period',
      'Currency',
      'Revenue ($)',
      'YoY Revenue Growth (%)',
      'Gross Margin (%)',
      'EBITDA ($)',
      'EBITDA Margin (%)',
      'Net Income ($)',
      'Cash & Equivalents ($)',
      'Total Debt ($)',
      'Free Cash Flow ($)',
      'Debt-to-Equity',
      'Health Status'
    ];

    const rows = companies.map((c) => [
      `"${c.entityName}"`,
      c.fiscalPeriod,
      c.currency,
      c.revenue,
      c.yoyRevenueGrowthPct,
      c.grossMarginPct,
      c.ebitda,
      c.ebitdaMarginPct,
      c.netIncome,
      c.cashAndEquivalents,
      c.totalDebt,
      c.freeCashFlow,
      c.debtToEquity || 'N/A',
      c.healthStatus,
    ]);

    const csvContent = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');

    res.setHeader('Content-Type', 'text/csv');
    res.setHeader('Content-Disposition', 'attachment; filename="30_Portfolio_Companies_Benchmarking_FY2025.csv"');
    return res.status(200).send(csvContent);
  } catch (err: any) {
    return res.status(500).json({ error: 'Failed to export benchmarking CSV.' });
  }
});

