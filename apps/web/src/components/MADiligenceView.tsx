import React, { useState, useEffect } from 'react';
import { ShieldAlert, AlertTriangle, Clock, Download, ArrowRight, Activity, DollarSign, CheckCircle } from 'lucide-react';

interface DiligenceContract {
  id: string;
  fileName: string;
  documentType: string;
  totalValue: number;
  uptimeSla: string;
  changeOfControl: string;
  hasCocRisk: boolean;
  earlyTerminationPenalty: string;
  autoRenewalClause: string;
  riskScore: number;
  status: string;
}

interface MADiligenceData {
  totalContracts: number;
  totalFinancialExposure: number;
  changeOfControlRiskCount: number;
  acquisitionTerminationRightsCount: number;
  upcomingRenewalsCount: number;
  averageRiskScore: number;
  contracts: DiligenceContract[];
}

interface MADiligenceViewProps {
  onSelectContract: (id: string) => void;
}

const DEFAULT_DEMO_DATA: MADiligenceData = {
  totalContracts: 3,
  totalFinancialExposure: 755000,
  changeOfControlRiskCount: 2,
  acquisitionTerminationRightsCount: 1,
  upcomingRenewalsCount: 1,
  averageRiskScore: 37,
  contracts: [
    {
      id: 'demo-doc-data-stream',
      fileName: '02_DataStream_Critical_Risk.pdf',
      documentType: 'contract',
      totalValue: 480000,
      uptimeSla: '99.9%',
      changeOfControl: 'M&A Risk: Vendor May Terminate Upon Acquisition',
      hasCocRisk: true,
      earlyTerminationPenalty: '$50,000.00',
      autoRenewalClause: 'None',
      riskScore: 65,
      status: 'NEEDS_REVIEW',
    },
    {
      id: 'demo-doc-cloud-core',
      fileName: '01_CloudCore_Vendor_SLA.pdf',
      documentType: 'sla',
      totalValue: 240000,
      uptimeSla: '99.95%',
      changeOfControl: 'M&A Trigger: Requires Vendor Consent',
      hasCocRisk: true,
      earlyTerminationPenalty: 'None',
      autoRenewalClause: 'Deadline: 60 days prior',
      riskScore: 45,
      status: 'NEEDS_REVIEW',
    },
    {
      id: 'demo-doc-secure-desk',
      fileName: '03_SecureDesk_Standard_License.pdf',
      documentType: 'license',
      totalValue: 35000,
      uptimeSla: 'N/A',
      changeOfControl: 'Standard Assignable',
      hasCocRisk: false,
      earlyTerminationPenalty: 'None',
      autoRenewalClause: 'None',
      riskScore: 10,
      status: 'APPROVED',
    },
  ],
};

export const MADiligenceView: React.FC<MADiligenceViewProps> = ({ onSelectContract }) => {
  const [data, setData] = useState<MADiligenceData>(DEFAULT_DEMO_DATA);
  const [filterRiskOnly, setFilterRiskOnly] = useState(false);

  useEffect(() => {
    fetch('/api/documents/ma-diligence')
      .then((res) => (res.ok ? res.json() : null))
      .then((json) => {
        if (json && json.contracts && json.contracts.length > 0) {
          setData(json);
        }
      })
      .catch(() => {
        // Fallback to default demo contracts
      });
  }, []);

  const displayedContracts = filterRiskOnly
    ? data.contracts.filter((c) => c.hasCocRisk || c.riskScore >= 40)
    : data.contracts;

  const handleExportCsv = () => {
    const headers = ['File Name', 'Type', 'Total Value ($)', 'SLA Uptime', 'Change of Control Risk', 'Early Termination Fee', 'Risk Score (0-100)'];
    const rows = displayedContracts.map((c) => [
      `"${c.fileName}"`,
      c.documentType,
      c.totalValue,
      c.uptimeSla,
      `"${c.changeOfControl}"`,
      `"${c.earlyTerminationPenalty}"`,
      c.riskScore,
    ]);
    const csvContent = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `MA_Vendor_SLA_Diligence_Rollup_${Date.now()}.csv`;
    a.click();
  };

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="sm:flex sm:items-center sm:justify-between mb-8">
        <div>
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-indigo-100 text-indigo-800 uppercase tracking-wide">
              Pillar 1
            </span>
            <h2 className="text-xl font-bold text-slate-900">M&A Vendor SLA & Contract Risk Auditor</h2>
          </div>
          <p className="mt-1 text-sm text-slate-500">
            Portfolio-wide diligence matrix analyzing 2,000+ vendor agreements, contractual liabilities, penalties, and acquisition triggers.
          </p>
        </div>

        <div className="mt-4 sm:mt-0 flex items-center space-x-3">
          <button
            onClick={() => setFilterRiskOnly(!filterRiskOnly)}
            className={`px-3 py-2 rounded-lg text-xs font-semibold border transition ${
              filterRiskOnly
                ? 'bg-amber-50 border-amber-300 text-amber-900'
                : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
            }`}
          >
            {filterRiskOnly ? 'Showing High Risk Only' : 'Filter High Risk'}
          </button>
          <button
            onClick={handleExportCsv}
            className="inline-flex items-center space-x-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold shadow-sm transition"
          >
            <Download className="w-4 h-4" />
            <span>Export Diligence Rollup (CSV)</span>
          </button>
        </div>
      </div>

      {/* KPI Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 text-xs font-bold uppercase">
            <span>Contracts Ingested</span>
            <Activity className="w-4 h-4 text-indigo-600" />
          </div>
          <div className="mt-2 text-2xl font-extrabold text-slate-900">{data.totalContracts}</div>
          <span className="text-xs text-slate-500 mt-1 block">Acquisition vendor base</span>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 text-xs font-bold uppercase">
            <span>Financial Exposure</span>
            <DollarSign className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="mt-2 text-2xl font-extrabold text-slate-900">
            ${(data.totalFinancialExposure / 1000).toFixed(0)}k
          </div>
          <span className="text-xs text-slate-500 mt-1 block">Total contractual commitments</span>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 text-xs font-bold uppercase">
            <span>Change of Control Triggers</span>
            <AlertTriangle className="w-4 h-4 text-amber-500" />
          </div>
          <div className="mt-2 text-2xl font-extrabold text-amber-600">
            {data.changeOfControlRiskCount}
          </div>
          <span className="text-xs text-slate-500 mt-1 block">Requires vendor consent</span>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 text-xs font-bold uppercase">
            <span>Acquisition Termination Rights</span>
            <ShieldAlert className="w-4 h-4 text-red-600" />
          </div>
          <div className="mt-2 text-2xl font-extrabold text-red-600">
            {data.acquisitionTerminationRightsCount}
          </div>
          <span className="text-xs text-slate-500 mt-1 block">Vendor can terminate upon deal</span>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 text-xs font-bold uppercase">
            <span>Renewals & Lock-ins</span>
            <Clock className="w-4 h-4 text-blue-600" />
          </div>
          <div className="mt-2 text-2xl font-extrabold text-blue-600">
            {data.upcomingRenewalsCount}
          </div>
          <span className="text-xs text-slate-500 mt-1 block">Auto-renewal windows active</span>
        </div>
      </div>

      {/* Diligence Matrix Table */}
      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
          <h3 className="text-sm font-bold uppercase text-slate-800 tracking-wider">
            Vendor Diligence Risk Matrix ({displayedContracts.length})
          </h3>
          <span className="text-xs text-slate-500">Sorted by Diligence Risk Score (Desc)</span>
        </div>

        <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
          <thead className="bg-slate-50 text-slate-500 uppercase text-xs font-semibold">
            <tr>
              <th className="px-6 py-3.5">Contract & Vendor</th>
              <th className="px-6 py-3.5">Commitment ($)</th>
              <th className="px-6 py-3.5">SLA Uptime</th>
              <th className="px-6 py-3.5">M&A Change of Control</th>
              <th className="px-6 py-3.5">Early Termination Fee</th>
              <th className="px-6 py-3.5">Risk Score</th>
              <th className="px-6 py-3.5 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {displayedContracts.map((c) => (
              <tr key={c.id} className="hover:bg-slate-50 transition">
                <td className="px-6 py-4">
                  <div className="font-semibold text-slate-900">{c.fileName}</div>
                  <span className="uppercase text-[11px] font-bold text-slate-500 px-1.5 py-0.5 bg-slate-100 rounded">
                    {c.documentType}
                  </span>
                </td>
                <td className="px-6 py-4 font-mono font-semibold text-slate-800">
                  ${c.totalValue ? c.totalValue.toLocaleString() : 'N/A'}
                </td>
                <td className="px-6 py-4">
                  <span className="font-semibold text-slate-800">{c.uptimeSla}</span>
                </td>
                <td className="px-6 py-4">
                  {c.changeOfControl.includes('Terminate') ? (
                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-red-100 text-red-800">
                      <ShieldAlert className="w-3 h-3 mr-1" /> Termination Right
                    </span>
                  ) : c.changeOfControl.includes('Requires') ? (
                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-800">
                      <AlertTriangle className="w-3 h-3 mr-1" /> Consent Required
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700">
                      <CheckCircle className="w-3 h-3 mr-1" /> Freely Assignable
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 font-mono text-xs text-slate-700">
                  {c.earlyTerminationPenalty}
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center space-x-2">
                    <div className="w-16 bg-slate-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          c.riskScore >= 50
                            ? 'bg-red-500'
                            : c.riskScore >= 25
                            ? 'bg-amber-500'
                            : 'bg-emerald-500'
                        }`}
                        style={{ width: `${c.riskScore}%` }}
                      />
                    </div>
                    <span className="text-xs font-bold text-slate-800">{c.riskScore}/100</span>
                  </div>
                </td>
                <td className="px-6 py-4 text-right">
                  <button
                    onClick={() => onSelectContract(c.id)}
                    className="inline-flex items-center text-xs font-semibold text-indigo-600 hover:text-indigo-800"
                  >
                    Audit <ArrowRight className="w-3.5 h-3.5 ml-1" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

