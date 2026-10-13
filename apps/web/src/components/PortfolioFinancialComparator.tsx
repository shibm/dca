import React, { useState, useEffect } from 'react';
import { TrendingUp, Download, Building2, AlertOctagon, CheckCircle2, DollarSign, Search, ArrowUpDown } from 'lucide-react';

interface CompanyBenchmark {
  entityName: string;
  fiscalPeriod: string;
  currency: string;
  revenue: number;
  yoyRevenueGrowthPct: number | null;
  grossMarginPct: number | null;
  ebitda: number;
  ebitdaMarginPct: number | null;
  netIncome: number;
  cashAndEquivalents: number;
  totalDebt: number;
  freeCashFlow: number;
  debtToEquity: number | null;
  healthStatus: 'EXCELLENT' | 'SOLID' | 'WATCHLIST' | 'DISTRESSED' | string;
  healthFlags: string[];
}

interface PortfolioData {
  totalEntitiesAnalyzed: number;
  reportingPeriod: string;
  totalPortfolioRevenue: number;
  averageGrossMarginPct: number;
  averageEbitdaMarginPct: number;
  medianRevenueGrowthPct: number;
  distressedEntitiesCount: number;
  watchlistEntitiesCount: number;
  companies: CompanyBenchmark[];
}

export const PortfolioFinancialComparator: React.FC = () => {
  const [data, setData] = useState<PortfolioData | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [sortField, setSortField] = useState<'revenue' | 'growth' | 'ebitdaMargin'>('revenue');

  useEffect(() => {
    fetch('/api/financials/portfolio-comparison')
      .then((res) => (res.ok ? res.json() : null))
      .then((json) => {
        if (json) setData(json);
      })
      .catch((err) => console.error(err));
  }, []);

  const handleExportCsv = () => {
    window.open('/api/financials/export-comparison', '_blank');
  };

  const companies = data?.companies || [];

  // Filter and sort
  const filtered = companies
    .filter((c) => {
      const matchesSearch = c.entityName.toLowerCase().includes(searchTerm.toLowerCase());
      if (statusFilter === 'ALL') return matchesSearch;
      if (statusFilter === 'HIGH_GROWTH') return matchesSearch && (c.yoyRevenueGrowthPct || 0) >= 20;
      return matchesSearch && c.healthStatus === statusFilter;
    })
    .sort((a, b) => {
      if (sortField === 'growth') {
        return (b.yoyRevenueGrowthPct || 0) - (a.yoyRevenueGrowthPct || 0);
      }
      if (sortField === 'ebitdaMargin') {
        return (b.ebitdaMarginPct || 0) - (a.ebitdaMarginPct || 0);
      }
      return b.revenue - a.revenue;
    });

  const getHealthBadge = (status: string) => {
    switch (status) {
      case 'EXCELLENT':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800">
            <CheckCircle2 className="w-3 h-3 mr-1" /> Excellent
          </span>
        );
      case 'SOLID':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-blue-100 text-blue-800">
            Solid
          </span>
        );
      case 'WATCHLIST':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-800">
            Watchlist
          </span>
        );
      case 'DISTRESSED':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-red-100 text-red-800">
            <AlertOctagon className="w-3 h-3 mr-1" /> Distressed
          </span>
        );
      default:
        return <span>{status}</span>;
    }
  };

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="sm:flex sm:items-center sm:justify-between mb-8">
        <div>
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 uppercase tracking-wide">
              Pillar 2
            </span>
            <h2 className="text-xl font-bold text-slate-900">Multi-Entity Portfolio Financial Comparator</h2>
          </div>
          <p className="mt-1 text-sm text-slate-500">
            Standardized financial statements across 30 portfolio companies. Compare revenue, EBITDA margins, cash burn, and balance sheet health side-by-side.
          </p>
        </div>

        <div className="mt-4 sm:mt-0 flex items-center space-x-3">
          <button
            onClick={handleExportCsv}
            className="inline-flex items-center space-x-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold shadow-sm transition"
          >
            <Download className="w-4 h-4" />
            <span>Export 30-Company Benchmarking (CSV)</span>
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 text-xs font-bold uppercase">
            <span>Portfolio Revenue</span>
            <DollarSign className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="mt-2 text-2xl font-extrabold text-slate-900">
            ${data ? (data.totalPortfolioRevenue / 1000000).toFixed(1) : '1,245.8'}M
          </div>
          <span className="text-xs text-slate-500 mt-1 block">Aggregated portfolio turnover</span>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 text-xs font-bold uppercase">
            <span>Avg Gross Margin</span>
            <TrendingUp className="w-4 h-4 text-indigo-600" />
          </div>
          <div className="mt-2 text-2xl font-extrabold text-indigo-600">
            {data ? data.averageGrossMarginPct : '58.4'}%
          </div>
          <span className="text-xs text-slate-500 mt-1 block">Normalized across GAAP/IFRS</span>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 text-xs font-bold uppercase">
            <span>Avg EBITDA Margin</span>
            <TrendingUp className="w-4 h-4 text-blue-600" />
          </div>
          <div className="mt-2 text-2xl font-extrabold text-blue-600">
            {data ? data.averageEbitdaMarginPct : '18.2'}%
          </div>
          <span className="text-xs text-slate-500 mt-1 block">Operating profitability</span>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 text-xs font-bold uppercase">
            <span>Median YoY Growth</span>
            <TrendingUp className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="mt-2 text-2xl font-extrabold text-emerald-600">
            +{data ? data.medianRevenueGrowthPct : '16.5'}%
          </div>
          <span className="text-xs text-slate-500 mt-1 block">Annual top-line expansion</span>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 text-xs font-bold uppercase">
            <span>Distressed / Burn</span>
            <AlertOctagon className="w-4 h-4 text-red-500" />
          </div>
          <div className="mt-2 text-2xl font-extrabold text-red-600">
            {data ? data.distressedEntitiesCount : '2'}
          </div>
          <span className="text-xs text-slate-500 mt-1 block">Negative FCF & high debt</span>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm mb-6 flex flex-wrap items-center justify-between gap-4">
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search portfolio company..."
            className="w-full text-xs pl-9 pr-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <div className="flex items-center space-x-2">
          {['ALL', 'EXCELLENT', 'SOLID', 'WATCHLIST', 'DISTRESSED', 'HIGH_GROWTH'].map((status) => (
            <button
              key={status}
              onClick={() => setStatusFilter(status)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                statusFilter === status
                  ? 'bg-slate-900 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {status === 'ALL' ? 'All (30)' : status === 'HIGH_GROWTH' ? 'High Growth (>20%)' : status}
            </button>
          ))}
        </div>

        <div className="flex items-center space-x-2 text-xs text-slate-500">
          <ArrowUpDown className="w-3.5 h-3.5" />
          <span>Sort:</span>
          <select
            value={sortField}
            onChange={(e) => setSortField(e.target.value as any)}
            className="text-xs font-semibold border border-slate-200 rounded px-2 py-1 bg-white focus:outline-none"
          >
            <option value="revenue">Highest Revenue</option>
            <option value="growth">Highest YoY Growth</option>
            <option value="ebitdaMargin">Highest EBITDA %</option>
          </select>
        </div>
      </div>

      {/* 30-Company Benchmarking Grid */}
      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
        <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
          <thead className="bg-slate-50 text-slate-500 uppercase text-xs font-semibold">
            <tr>
              <th className="px-6 py-3.5">Company & Period</th>
              <th className="px-6 py-3.5">Revenue ($)</th>
              <th className="px-6 py-3.5">YoY Growth</th>
              <th className="px-6 py-3.5">Gross Margin</th>
              <th className="px-6 py-3.5">EBITDA & Margin</th>
              <th className="px-6 py-3.5">Free Cash Flow</th>
              <th className="px-6 py-3.5">Cash / Debt</th>
              <th className="px-6 py-3.5 text-right">Health Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {filtered.map((company, idx) => {
              const isHighGrowth = (company.yoyRevenueGrowthPct || 0) >= 20;
              const isNegativeEbitda = company.ebitda < 0;

              return (
                <tr key={company.entityName} className="hover:bg-slate-50 transition">
                  <td className="px-6 py-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-7 h-7 rounded-lg bg-indigo-50 text-indigo-700 flex items-center justify-center font-bold text-xs flex-shrink-0">
                        {idx + 1}
                      </div>
                      <div>
                        <div className="font-semibold text-slate-900">{company.entityName}</div>
                        <span className="text-xs text-slate-500">{company.fiscalPeriod} • {company.currency}</span>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 font-mono font-semibold text-slate-800">
                    ${(company.revenue / 1000000).toFixed(1)}M
                  </td>
                  <td className="px-6 py-4">
                    {company.yoyRevenueGrowthPct !== null ? (
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-bold ${
                          isHighGrowth
                            ? 'bg-emerald-100 text-emerald-800'
                            : company.yoyRevenueGrowthPct >= 0
                            ? 'bg-slate-100 text-slate-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {company.yoyRevenueGrowthPct >= 0 ? '+' : ''}{company.yoyRevenueGrowthPct.toFixed(1)}%
                      </span>
                    ) : (
                      <span className="text-slate-400">N/A</span>
                    )}
                  </td>
                  <td className="px-6 py-4 font-mono text-xs text-slate-700">
                    {company.grossMarginPct ? `${company.grossMarginPct.toFixed(1)}%` : 'N/A'}
                  </td>
                  <td className="px-6 py-4">
                    <div className="font-mono text-xs font-semibold text-slate-800">
                      ${(company.ebitda / 1000000).toFixed(1)}M
                    </div>
                    <div className={`text-[11px] ${isNegativeEbitda ? 'text-red-600 font-bold' : 'text-slate-500'}`}>
                      {company.ebitdaMarginPct ? `${company.ebitdaMarginPct.toFixed(1)}%` : 'N/A'} margin
                    </div>
                  </td>
                  <td className="px-6 py-4 font-mono text-xs">
                    <span className={company.freeCashFlow < 0 ? 'text-red-600 font-bold' : 'text-slate-800 font-semibold'}>
                      ${(company.freeCashFlow / 1000000).toFixed(1)}M
                    </span>
                  </td>
                  <td className="px-6 py-4 text-xs font-mono text-slate-600">
                    <div>Cash: ${(company.cashAndEquivalents / 1000000).toFixed(1)}M</div>
                    <div className="text-slate-400">Debt: ${(company.totalDebt / 1000000).toFixed(1)}M</div>
                  </td>
                  <td className="px-6 py-4 text-right">
                    {getHealthBadge(company.healthStatus)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

