import React, { useState, useEffect } from 'react';
import {
  Cpu,
  AlertTriangle,
  CheckCircle2,
  FileCheck2,
  Download,
  Play,
  RotateCw,
  Search,
  Filter,
  DollarSign,
  TrendingDown,
  TrendingUp,
  AlertOctagon,
  Copy,
  Layers,
  Sparkles,
} from 'lucide-react';

interface ScriptMetadata {
  script_id: string;
  name: string;
  category: string;
  description: string;
  version: string;
  tags: string[];
}

interface DataAnomaly {
  anomaly_id: string;
  record_index: number;
  record_id?: string;
  field_name?: string;
  anomaly_type: string;
  severity: 'CRITICAL' | 'HIGH' | 'WARNING' | 'MEDIUM' | 'INFO';
  description: string;
  original_value?: any;
  suggested_value?: any;
  z_score?: number;
  confidence_score?: number;
}

interface BusinessInsight {
  insight_id: string;
  title: string;
  category: string;
  metric_type: string;
  metric_value: number;
  formatted_value: string;
  narrative: string;
  recommendation: string;
  trend: 'UP' | 'DOWN' | 'NEUTRAL' | 'RISK';
}

interface ScriptExecutionLog {
  script_id: string;
  script_name: string;
  execution_time_ms: number;
  status: 'SUCCESS' | 'FAILED' | 'SKIPPED';
  records_processed: number;
  anomalies_flagged: number;
  insights_generated: number;
}

interface JobResult {
  job_id: string;
  status: string;
  execution_time_ms: number;
  total_records_ingested: number;
  cleaned_records_count: number;
  duplicates_detected: number;
  anomalies_count: number;
  critical_anomalies_count: number;
  anomalies: DataAnomaly[];
  insights: BusinessInsight[];
  script_logs: ScriptExecutionLog[];
  sample_cleaned_records: any[];
}

export const AutomationScriptRunner: React.FC = () => {
  const [scripts, setScripts] = useState<ScriptMetadata[]>([]);
  const [selectedScriptIds, setSelectedScriptIds] = useState<string[]>([]);
  const [jobResult, setJobResult] = useState<JobResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [severityFilter, setSeverityFilter] = useState<string>('ALL');
  const [typeFilter, setTypeFilter] = useState<string>('ALL');
  const [activeTab, setActiveTab] = useState<'anomalies' | 'insights' | 'scripts' | 'records'>('anomalies');

  // Load scripts and run initial benchmark job
  useEffect(() => {
    fetch('/api/automation/scripts')
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data?.scripts) {
          setScripts(data.scripts);
          setSelectedScriptIds(data.scripts.map((s: ScriptMetadata) => s.script_id));
        }
      })
      .catch(() => {});

    // Automatically trigger benchmark run
    runBenchmarkJob();
  }, []);

  const runBenchmarkJob = async () => {
    setIsLoading(true);
    try {
      const sampleRes = await fetch('/api/automation/sample-data');
      const sampleData = await sampleRes.json();
      const records = sampleData.records || [];

      const runRes = await fetch('/api/automation/jobs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          script_ids: selectedScriptIds.length > 0 ? selectedScriptIds : undefined,
          raw_records: records,
        }),
      });

      if (runRes.ok) {
        const result = await runRes.json();
        setJobResult(result);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleScript = (id: string) => {
    setSelectedScriptIds((prev) =>
      prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]
    );
  };

  const handleExportCSV = () => {
    window.open('/api/automation/export-anomalies', '_blank');
  };

  // Filtered anomalies
  const filteredAnomalies = (jobResult?.anomalies || []).filter((a) => {
    const matchesSearch =
      searchQuery === '' ||
      a.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (a.record_id && a.record_id.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (a.field_name && a.field_name.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesSeverity =
      severityFilter === 'ALL' || a.severity.toUpperCase() === severityFilter.toUpperCase();

    const matchesType = typeFilter === 'ALL' || a.anomaly_type === typeFilter;

    return matchesSearch && matchesSeverity && matchesType;
  });

  const getSeverityBadge = (severity: string) => {
    switch (severity.toUpperCase()) {
      case 'CRITICAL':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'HIGH':
        return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'WARNING':
      case 'MEDIUM':
        return 'bg-amber-100 text-amber-800 border-amber-300';
      default:
        return 'bg-slate-100 text-slate-800 border-slate-300';
    }
  };

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 space-y-6">
      {/* Top Banner */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-3 mb-1">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300">
                PILLAR 4
              </span>
              <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
                Batch Data Automation & Python Script Engine
              </h1>
            </div>
            <p className="text-sm text-slate-500">
              Cross-department data normalizer, enterprise business rule validator, and pluggable Python analytics execution framework.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={runBenchmarkJob}
              disabled={isLoading}
              className="inline-flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-semibold hover:bg-indigo-700 transition shadow-sm disabled:opacity-50"
            >
              {isLoading ? (
                <RotateCw className="w-4 h-4 animate-spin" />
              ) : (
                <Play className="w-4 h-4" />
              )}
              <span>Run Batch Engine</span>
            </button>

            <button
              onClick={handleExportCSV}
              className="inline-flex items-center space-x-2 px-4 py-2 bg-white text-slate-700 border border-slate-300 rounded-lg text-sm font-semibold hover:bg-slate-50 transition shadow-sm"
            >
              <Download className="w-4 h-4 text-slate-500" />
              <span>Export Anomalies CSV</span>
            </button>
          </div>
        </div>

        {/* KPI Metrics Strip */}
        {jobResult && (
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mt-6 pt-6 border-t border-slate-100">
            <div className="bg-slate-50 rounded-lg p-3.5 border border-slate-200">
              <span className="text-xs font-medium text-slate-500 block">Total Records Ingested</span>
              <span className="text-xl font-bold text-slate-900">{jobResult.total_records_ingested}</span>
              <span className="text-xs text-slate-400 block mt-0.5">Multi-department sources</span>
            </div>

            <div className="bg-slate-50 rounded-lg p-3.5 border border-slate-200">
              <span className="text-xs font-medium text-slate-500 block">Cleaned & Normalized</span>
              <span className="text-xl font-bold text-emerald-700">{jobResult.cleaned_records_count}</span>
              <span className="text-xs text-emerald-600 block mt-0.5">Canonical schema mapped</span>
            </div>

            <div className="bg-slate-50 rounded-lg p-3.5 border border-slate-200">
              <span className="text-xs font-medium text-slate-500 block">Duplicates Detected</span>
              <span className="text-xl font-bold text-amber-600">{jobResult.duplicates_detected}</span>
              <span className="text-xs text-amber-600 block mt-0.5">Exact & key duplicates</span>
            </div>

            <div className="bg-slate-50 rounded-lg p-3.5 border border-slate-200">
              <span className="text-xs font-medium text-slate-500 block">Total Anomalies</span>
              <span className="text-xl font-bold text-red-600">{jobResult.anomalies_count}</span>
              <span className="text-xs text-red-600 block mt-0.5">{jobResult.critical_anomalies_count} Critical severity</span>
            </div>

            <div className="bg-slate-50 rounded-lg p-3.5 border border-slate-200">
              <span className="text-xs font-medium text-slate-500 block">Execution Speed</span>
              <span className="text-xl font-bold text-indigo-700">{jobResult.execution_time_ms} ms</span>
              <span className="text-xs text-indigo-600 block mt-0.5">{jobResult.script_logs.length} Scripts executed</span>
            </div>
          </div>
        )}
      </div>

      {/* Navigation Sub-Tabs */}
      <div className="flex border-b border-slate-200 space-x-6">
        <button
          onClick={() => setActiveTab('anomalies')}
          className={`pb-3 text-sm font-semibold flex items-center space-x-2 border-b-2 transition ${
            activeTab === 'anomalies'
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <AlertTriangle className="w-4 h-4" />
          <span>Anomalies & Policy Breaches ({jobResult?.anomalies_count || 0})</span>
        </button>

        <button
          onClick={() => setActiveTab('insights')}
          className={`pb-3 text-sm font-semibold flex items-center space-x-2 border-b-2 transition ${
            activeTab === 'insights'
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Sparkles className="w-4 h-4" />
          <span>Strategic Business Insights ({jobResult?.insights?.length || 0})</span>
        </button>

        <button
          onClick={() => setActiveTab('scripts')}
          className={`pb-3 text-sm font-semibold flex items-center space-x-2 border-b-2 transition ${
            activeTab === 'scripts'
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Cpu className="w-4 h-4" />
          <span>Python Plugin Registry ({scripts.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('records')}
          className={`pb-3 text-sm font-semibold flex items-center space-x-2 border-b-2 transition ${
            activeTab === 'records'
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Layers className="w-4 h-4" />
          <span>Normalized Dataset Preview</span>
        </button>
      </div>

      {/* TAB 1: ANOMALIES & POLICY BREACHES */}
      {activeTab === 'anomalies' && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          {/* Filter Bar */}
          <div className="p-4 bg-slate-50 border-b border-slate-200 flex flex-col md:flex-row gap-3 items-center justify-between">
            <div className="relative flex-1 w-full">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="text"
                placeholder="Search anomalies by vendor, record ID, or rule description..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-4 py-2 bg-white border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div className="flex items-center space-x-3 w-full md:w-auto">
              <div className="flex items-center space-x-2">
                <Filter className="w-4 h-4 text-slate-500" />
                <span className="text-xs font-semibold text-slate-600">Severity:</span>
                <select
                  value={severityFilter}
                  onChange={(e) => setSeverityFilter(e.target.value)}
                  className="bg-white border border-slate-300 rounded-md text-xs py-1.5 px-2.5 font-medium text-slate-700"
                >
                  <option value="ALL">All Severities</option>
                  <option value="CRITICAL">Critical</option>
                  <option value="HIGH">High</option>
                  <option value="WARNING">Warning</option>
                  <option value="INFO">Info</option>
                </select>
              </div>

              <div className="flex items-center space-x-2">
                <span className="text-xs font-semibold text-slate-600">Type:</span>
                <select
                  value={typeFilter}
                  onChange={(e) => setTypeFilter(e.target.value)}
                  className="bg-white border border-slate-300 rounded-md text-xs py-1.5 px-2.5 font-medium text-slate-700"
                >
                  <option value="ALL">All Anomaly Types</option>
                  <option value="DUPLICATE_RECORD">Duplicate Record</option>
                  <option value="MISSING_MANDATORY_FIELD">Missing PO / Mandatory Field</option>
                  <option value="THRESHOLD_VIOLATION">Threshold Violation</option>
                  <option value="SUSPICIOUS_PATTERN">Suspicious Pattern</option>
                  <option value="Z_SCORE_OUTLIER">Statistical Z-Score Outlier</option>
                  <option value="CROSS_FIELD_INCONSISTENCY">Cross-Field Inconsistency</option>
                </select>
              </div>
            </div>
          </div>

          {/* Anomalies Table */}
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Severity
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Record ID / Target
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Anomaly Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Rule Trigger & Description
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Value / Action
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-200">
                {filteredAnomalies.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-10 text-center text-sm text-slate-500">
                      No anomalies matching current search and filter criteria.
                    </td>
                  </tr>
                ) : (
                  filteredAnomalies.map((anom) => (
                    <tr key={anom.anomaly_id} className="hover:bg-slate-50 transition">
                      <td className="px-4 py-3.5 whitespace-nowrap">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-bold border ${getSeverityBadge(
                            anom.severity
                          )}`}
                        >
                          {anom.severity}
                        </span>
                      </td>

                      <td className="px-4 py-3.5 whitespace-nowrap">
                        <div className="text-xs font-mono font-medium text-slate-800">
                          {anom.record_id || `Rec #${anom.record_index}`}
                        </div>
                        {anom.field_name && (
                          <div className="text-xs text-slate-400">Field: {anom.field_name}</div>
                        )}
                      </td>

                      <td className="px-4 py-3.5 whitespace-nowrap">
                        <span className="text-xs font-semibold text-slate-700 bg-slate-100 px-2 py-1 rounded">
                          {anom.anomaly_type.replace(/_/g, ' ')}
                        </span>
                      </td>

                      <td className="px-6 py-3.5">
                        <p className="text-xs text-slate-800 font-medium leading-relaxed">
                          {anom.description}
                        </p>
                        {anom.z_score !== undefined && anom.z_score !== null && (
                          <span className="inline-block mt-1 text-[11px] font-mono text-purple-700 bg-purple-50 px-1.5 py-0.5 rounded border border-purple-200">
                            Z-Score: {anom.z_score.toFixed(2)}σ
                          </span>
                        )}
                      </td>

                      <td className="px-4 py-3.5 whitespace-nowrap">
                        {anom.suggested_value ? (
                          <div className="text-xs text-indigo-700 font-medium bg-indigo-50 px-2 py-1 rounded border border-indigo-200">
                            Action: {anom.suggested_value}
                          </div>
                        ) : (
                          <span className="text-xs font-mono text-slate-500">
                            Val: {String(anom.original_value || 'N/A')}
                          </span>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 2: STRATEGIC BUSINESS INSIGHTS */}
      {activeTab === 'insights' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {(jobResult?.insights || []).map((ins) => (
            <div
              key={ins.insight_id}
              className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    {ins.category}
                  </span>
                  <span
                    className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-bold ${
                      ins.trend === 'RISK'
                        ? 'bg-red-100 text-red-800'
                        : ins.trend === 'UP'
                        ? 'bg-emerald-100 text-emerald-800'
                        : 'bg-slate-100 text-slate-700'
                    }`}
                  >
                    {ins.trend === 'RISK' && <AlertOctagon className="w-3 h-3 mr-1" />}
                    {ins.trend === 'UP' && <TrendingUp className="w-3 h-3 mr-1" />}
                    {ins.formatted_value}
                  </span>
                </div>

                <h3 className="text-base font-bold text-slate-900 mb-2">{ins.title}</h3>
                <p className="text-xs text-slate-600 leading-relaxed mb-4">{ins.narrative}</p>
              </div>

              <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
                <span className="text-xs font-semibold text-indigo-700 block mb-0.5">
                  Recommendation:
                </span>
                <p className="text-xs text-slate-700">{ins.recommendation}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* TAB 3: PYTHON SCRIPT REGISTRY */}
      {activeTab === 'scripts' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {scripts.map((script) => {
            const isSelected = selectedScriptIds.includes(script.script_id);
            const scriptLog = jobResult?.script_logs.find((l) => l.script_id === script.script_id);

            return (
              <div
                key={script.script_id}
                className={`bg-white rounded-xl border p-6 transition ${
                  isSelected ? 'border-indigo-600 shadow-sm' : 'border-slate-200 opacity-75'
                }`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded">
                      {script.category}
                    </span>
                    <h3 className="text-base font-bold text-slate-900 mt-1">{script.name}</h3>
                    <span className="text-xs text-slate-400 font-mono">v{script.version}</span>
                  </div>

                  <button
                    onClick={() => toggleScript(script.script_id)}
                    className={`px-3 py-1 text-xs font-semibold rounded-md transition ${
                      isSelected
                        ? 'bg-indigo-600 text-white'
                        : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                    }`}
                  >
                    {isSelected ? 'Enabled' : 'Disabled'}
                  </button>
                </div>

                <p className="text-xs text-slate-600 mb-4 leading-relaxed">{script.description}</p>

                <div className="flex flex-wrap gap-1.5 mb-4">
                  {script.tags.map((tag) => (
                    <span
                      key={tag}
                      className="text-[10px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>

                {scriptLog && (
                  <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200 flex justify-between items-center text-xs">
                    <span className="text-slate-500 font-mono">
                      Runtime: {scriptLog.execution_time_ms}ms
                    </span>
                    <div className="flex space-x-3">
                      <span className="text-red-600 font-semibold">
                        {scriptLog.anomalies_flagged} anomalies
                      </span>
                      <span className="text-indigo-600 font-semibold">
                        {scriptLog.insights_generated} insights
                      </span>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* TAB 4: NORMALIZED DATASET PREVIEW */}
      {activeTab === 'records' && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200">
            <h3 className="text-sm font-bold text-slate-800">
              Canonical Normalized Records Preview (First 20 items)
            </h3>
            <p className="text-xs text-slate-500">
              Inconsistent multi-department columns mapped to standardized schema attributes.
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">
                    Vendor / Entity
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">
                    Invoice ID
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">
                    Amount
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">
                    Date
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">
                    PO Number
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">
                    Department
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-200 font-mono text-xs">
                {(jobResult?.sample_cleaned_records || []).map((rec, i) => (
                  <tr
                    key={i}
                    className={`hover:bg-slate-50 ${rec._is_duplicate ? 'bg-amber-50/60' : ''}`}
                  >
                    <td className="px-4 py-2.5 font-sans font-medium text-slate-900">
                      {rec.vendor_name || 'N/A'}
                      {rec._is_duplicate && (
                        <span className="ml-2 px-1.5 py-0.5 text-[10px] bg-amber-200 text-amber-800 rounded font-bold font-sans">
                          DUPLICATE
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-2.5 text-slate-600">{rec.invoice_id || 'N/A'}</td>
                    <td className="px-4 py-2.5 font-bold text-slate-900">
                      {rec.amount !== undefined && rec.amount !== null
                        ? `$${Number(rec.amount).toLocaleString(undefined, {
                            minimumFractionDigits: 2,
                          })}`
                        : 'N/A'}
                    </td>
                    <td className="px-4 py-2.5 text-slate-600">{rec.date || 'N/A'}</td>
                    <td className="px-4 py-2.5 text-slate-600">
                      {rec.po_number || (
                        <span className="text-red-500 font-sans font-semibold">MISSING</span>
                      )}
                    </td>
                    <td className="px-4 py-2.5 font-sans text-slate-600">{rec.department || 'General'}</td>
                    <td className="px-4 py-2.5">
                      <span className="px-2 py-0.5 rounded text-[10px] font-sans font-bold bg-slate-100 text-slate-700">
                        {rec.status || 'UNSPECIFIED'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

