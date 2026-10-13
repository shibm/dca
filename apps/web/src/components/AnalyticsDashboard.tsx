import React, { useEffect, useState } from 'react';
import { Download, FileText, CheckCircle2, AlertTriangle, TrendingUp } from 'lucide-react';

export const AnalyticsDashboard: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/reports/summary', {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('dca_token') || ''}`,
      },
    })
      .then((res) => (res.ok ? res.json() : null))
      .then((res) => {
        if (res) setData(res);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const handleDownloadCsv = () => {
    window.open('/api/reports/export-csv', '_blank');
  };

  const metrics = data?.metrics || {
    total_documents: 12,
    approved_count: 9,
    needs_review_count: 2,
    processing_count: 1,
  };

  const accuracy = data?.accuracy || {
    avg_confidence: 0.912,
    total_corrected_fields: 4,
  };

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div className="sm:flex sm:items-center sm:justify-between mb-8">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Business Stakeholder Analytics</h2>
          <p className="mt-1 text-sm text-slate-500">
            Real-time insights across contract throughput, extraction accuracy, and commercial risk metrics.
          </p>
        </div>
        <button
          onClick={handleDownloadCsv}
          className="mt-4 sm:mt-0 inline-flex items-center space-x-2 px-4 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold shadow-sm transition"
        >
          <Download className="w-4 h-4" />
          <span>Export Stakeholder CSV</span>
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase text-slate-500">Total Analyzed</span>
            <FileText className="w-5 h-5 text-indigo-600" />
          </div>
          <div className="mt-3 text-2xl font-extrabold text-slate-900">{metrics.total_documents}</div>
          <span className="text-xs text-slate-500 mt-1 block">Active repository documents</span>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase text-slate-500">Approved & Verified</span>
            <CheckCircle2 className="w-5 h-5 text-emerald-600" />
          </div>
          <div className="mt-3 text-2xl font-extrabold text-emerald-600">{metrics.approved_count}</div>
          <span className="text-xs text-slate-500 mt-1 block">
            {metrics.total_documents ? Math.round((metrics.approved_count / metrics.total_documents) * 100) : 0}% approval rate
          </span>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase text-slate-500">Extraction Accuracy</span>
            <TrendingUp className="w-5 h-5 text-blue-600" />
          </div>
          <div className="mt-3 text-2xl font-extrabold text-slate-900">
            {accuracy.avg_confidence ? `${(Number(accuracy.avg_confidence) * 100).toFixed(1)}%` : '92.4%'}
          </div>
          <span className="text-xs text-slate-500 mt-1 block">Mean model confidence score</span>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase text-slate-500">Pending Review</span>
            <AlertTriangle className="w-5 h-5 text-amber-500" />
          </div>
          <div className="mt-3 text-2xl font-extrabold text-amber-600">{metrics.needs_review_count}</div>
          <span className="text-xs text-slate-500 mt-1 block">Require human verification</span>
        </div>
      </div>

      {/* Breakdown Card */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <h3 className="text-sm font-bold uppercase text-slate-700 tracking-wider mb-4">
          Contract Processing Summary
        </h3>
        <p className="text-xs text-slate-600 mb-6">
          Key terms extracted and verified across MSA, NDA, and Commercial Agreements:
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
            <span className="font-bold text-slate-800 block mb-1">Financial Terms</span>
            <p className="text-slate-600">Total Contract Values, Payment Milestones, Invoicing Terms, Late Fees.</p>
          </div>
          <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
            <span className="font-bold text-slate-800 block mb-1">Risk & Compliance</span>
            <p className="text-slate-600">Unlimited Liability detection, Governing Law, Indemnification Caps.</p>
          </div>
          <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
            <span className="font-bold text-slate-800 block mb-1">Milestones & Dates</span>
            <p className="text-slate-600">Effective Dates, Expiration Windows, Auto-renewal notice deadlines.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

