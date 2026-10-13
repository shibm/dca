import React, { useState, useEffect } from 'react';
import { BookOpen, CheckCircle2, FileCheck, Layers, DollarSign, Download, Edit3, ShieldAlert } from 'lucide-react';

export const AccountingMemoStudio: React.FC = () => {
  const [memo, setMemo] = useState<any>(null);
  const [activeSubTab, setActiveSubTab] = useState<'5steps' | 'journalEntries' | 'fullMemo'>('5steps');
  const [isEditing, setIsEditing] = useState(false);
  const [editedExecutiveSummary, setEditedExecutiveSummary] = useState('');
  const [isApproved, setIsApproved] = useState(false);

  useEffect(() => {
    fetch('/api/accounting/memos/demo-memo-1')
      .then((res) => (res.ok ? res.json() : null))
      .then((json) => {
        if (json?.memo) {
          setMemo(json.memo);
          setEditedExecutiveSummary(json.memo.executiveSummary);
          setIsApproved(json.memo.status === 'APPROVED');
        }
      })
      .catch((err) => console.error(err));
  }, []);

  const handleApprove = async () => {
    try {
      await fetch('/api/accounting/memos/demo-memo-1/approve', { method: 'POST' });
    } catch {}
    setIsApproved(true);
    if (memo) setMemo({ ...memo, status: 'APPROVED', reviewedBy: 'Senior Accounting Manager, CPA' });
  };

  const handleExport = () => {
    if (!memo) return;
    const memoContent = `
================================================================================
TECHNICAL ACCOUNTING MEMORANDUM
Standard: ASC 606 (Revenue from Contracts with Customers)
Reference: ${memo.memoId}
Status: ${isApproved ? 'APPROVED / AUDIT-READY' : 'DRAFT'}
================================================================================

Contract: ${memo.contractTitle}
Parties: ${memo.parties.join(' and ')}
Contract Value: $${memo.contractValue.toLocaleString()} USD
Effective Date: ${memo.effectiveDate}

EXECUTIVE SUMMARY
-----------------
${editedExecutiveSummary || memo.executiveSummary}

ASC 606 5-STEP EVALUATION
-------------------------
Step 1: Contract Identification
${memo.asc606Analysis.step1Assessment}

Step 2: Performance Obligations
${memo.asc606Analysis.step2Assessment}

Step 3: Determine Transaction Price
${memo.asc606Analysis.step3Assessment}

Step 4: Allocate Transaction Price
${memo.asc606Analysis.step4Assessment}

Step 5: Revenue Timing & Recognition
${memo.asc606Analysis.step5RecognitionSummary}

SUGGESTED BALANCED JOURNAL ENTRIES
----------------------------------
${memo.suggestedJournalEntries.map((je: any) => `
[${je.scheduleId}] ${je.eventName} (${je.period}) - ${je.isBalanced ? 'BALANCED' : 'UNBALANCED'}
Total Debits: $${je.totalDebit.toLocaleString()} | Total Credits: $${je.totalCredit.toLocaleString()}
${je.lines.map((l: any) => `  ${l.accountName.padEnd(45)} Debit: $${(l.debit || 0).toLocaleString().padStart(10)} | Credit: $${(l.credit || 0).toLocaleString().padStart(10)}`).join('\n')}
`).join('\n')}

CONCLUSION & AUDIT DISCLOSURES
------------------------------
${memo.conclusionAndDisclosures}
    `;

    const blob = new Blob([memoContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Technical_Accounting_Memo_ASC606_${Date.now()}.txt`;
    a.click();
  };

  if (!memo) {
    return (
      <div className="max-w-7xl mx-auto py-12 px-4 text-center">
        <BookOpen className="w-8 h-8 text-indigo-600 animate-spin mx-auto mb-2" />
        <p className="text-sm text-slate-500">Loading technical accounting memorandum...</p>
      </div>
    );
  }

  const analysis = memo.asc606Analysis;
  const journalEntries = memo.suggestedJournalEntries || [];

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      {/* Top Action Bar */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm mb-6">
        <div className="sm:flex sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center space-x-2">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-purple-100 text-purple-800 uppercase tracking-wide">
                Pillar 3
              </span>
              <span className="text-xs font-mono font-semibold text-slate-500">{memo.memoId}</span>
              <span
                className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
                  isApproved
                    ? 'bg-emerald-100 text-emerald-800'
                    : 'bg-amber-100 text-amber-800'
                }`}
              >
                {isApproved ? 'Approved / Audit-Ready' : 'Draft / Expert Review'}
              </span>
            </div>
            <h2 className="text-xl font-bold text-slate-900 mt-1">{memo.contractTitle}</h2>
            <div className="flex items-center space-x-2 text-xs text-slate-500 mt-1">
              <span>Parties: <strong className="text-slate-800">{memo.parties.join(' vs ')}</strong></span>
              <span>•</span>
              <span>Contract Value: <strong className="text-slate-900 font-mono">${memo.contractValue.toLocaleString()} {memo.currency}</strong></span>
              <span>•</span>
              <span>Effective: <strong className="text-slate-800">{memo.effectiveDate}</strong></span>
            </div>
          </div>

          <div className="mt-4 sm:mt-0 flex items-center space-x-3">
            <button
              onClick={handleExport}
              className="inline-flex items-center space-x-2 px-3.5 py-2 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-semibold transition"
            >
              <Download className="w-4 h-4" />
              <span>Export Memo</span>
            </button>
            <button
              onClick={handleApprove}
              disabled={isApproved}
              className="inline-flex items-center space-x-2 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold shadow-sm transition disabled:opacity-50"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>{isApproved ? 'Sign-Off Complete' : 'Sign-Off & Approve'}</span>
            </button>
          </div>
        </div>

        {/* Sub Navigation */}
        <div className="mt-6 flex border-b border-slate-200">
          <button
            onClick={() => setActiveSubTab('5steps')}
            className={`pb-3 px-4 text-xs font-bold transition flex items-center space-x-2 border-b-2 ${
              activeSubTab === '5steps'
                ? 'border-indigo-600 text-indigo-700'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <Layers className="w-4 h-4" />
            <span>ASC 606 5-Step Model</span>
          </button>
          <button
            onClick={() => setActiveSubTab('journalEntries')}
            className={`pb-3 px-4 text-xs font-bold transition flex items-center space-x-2 border-b-2 ${
              activeSubTab === 'journalEntries'
                ? 'border-indigo-600 text-indigo-700'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <DollarSign className="w-4 h-4" />
            <span>Debit / Credit Journal Entries ({journalEntries.length})</span>
          </button>
          <button
            onClick={() => setActiveSubTab('fullMemo')}
            className={`pb-3 px-4 text-xs font-bold transition flex items-center space-x-2 border-b-2 ${
              activeSubTab === 'fullMemo'
                ? 'border-indigo-600 text-indigo-700'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <BookOpen className="w-4 h-4" />
            <span>Executive Memo & Disclosures</span>
          </button>
        </div>
      </div>

      {/* SubTab 1: ASC 606 5-Step Model */}
      {activeSubTab === '5steps' && (
        <div className="space-y-6">
          {/* Step 1 */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <div className="flex items-center space-x-2 mb-2">
              <span className="w-6 h-6 rounded-full bg-indigo-50 text-indigo-700 font-bold text-xs flex items-center justify-center">1</span>
              <h3 className="text-sm font-bold text-slate-900 uppercase">Step 1: Identify the Contract with a Customer</h3>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed pl-8">
              {analysis.step1Assessment}
            </p>
          </div>

          {/* Step 2 */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <div className="flex items-center space-x-2 mb-4">
              <span className="w-6 h-6 rounded-full bg-indigo-50 text-indigo-700 font-bold text-xs flex items-center justify-center">2</span>
              <h3 className="text-sm font-bold text-slate-900 uppercase">Step 2: Identify the Performance Obligations in the Contract</h3>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed pl-8 mb-4">
              {analysis.step2Assessment}
            </p>

            <div className="pl-8 space-y-3">
              {analysis.step2PerformanceObligations.map((p: any) => (
                <div key={p.id} className="p-4 rounded-lg bg-slate-50 border border-slate-200 flex flex-col md:flex-row md:items-center justify-between gap-3">
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-indigo-100 text-indigo-800">{p.id}</span>
                      <span className="text-xs font-bold text-slate-900">{p.name}</span>
                    </div>
                    <p className="text-[11px] text-slate-500 italic mt-1">"{p.contractCitation}"</p>
                  </div>
                  <div className="text-right flex-shrink-0 text-xs">
                    <div className="font-mono font-bold text-slate-900">${p.allocatedTransactionPrice.toLocaleString()} USD</div>
                    <span className="text-[11px] font-semibold text-indigo-600 uppercase">{p.timingOfSatisfaction} ({p.recognitionPeriod})</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Step 3 & 4 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
              <div className="flex items-center space-x-2 mb-2">
                <span className="w-6 h-6 rounded-full bg-indigo-50 text-indigo-700 font-bold text-xs flex items-center justify-center">3</span>
                <h3 className="text-sm font-bold text-slate-900 uppercase">Step 3: Determine Transaction Price</h3>
              </div>
              <p className="text-xs text-slate-600 leading-relaxed pl-8">
                {analysis.step3Assessment}
              </p>
            </div>

            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
              <div className="flex items-center space-x-2 mb-2">
                <span className="w-6 h-6 rounded-full bg-indigo-50 text-indigo-700 font-bold text-xs flex items-center justify-center">4</span>
                <h3 className="text-sm font-bold text-slate-900 uppercase">Step 4: Allocate Transaction Price</h3>
              </div>
              <p className="text-xs text-slate-600 leading-relaxed pl-8">
                {analysis.step4Assessment}
              </p>
            </div>
          </div>

          {/* Step 5 */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <div className="flex items-center space-x-2 mb-2">
              <span className="w-6 h-6 rounded-full bg-indigo-50 text-indigo-700 font-bold text-xs flex items-center justify-center">5</span>
              <h3 className="text-sm font-bold text-slate-900 uppercase">Step 5: Recognize Revenue when Performance Obligation is Satisfied</h3>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed pl-8">
              {analysis.step5RecognitionSummary}
            </p>
          </div>
        </div>
      )}

      {/* SubTab 2: Suggested Journal Entries */}
      {activeSubTab === 'journalEntries' && (
        <div className="space-y-6">
          {journalEntries.map((je: any) => (
            <div key={je.scheduleId} className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
              <div className="px-6 py-4 bg-slate-50 border-b border-slate-200 flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center space-x-3">
                  <span className="px-2 py-0.5 rounded text-xs font-mono font-bold bg-slate-900 text-white">
                    {je.scheduleId}
                  </span>
                  <div>
                    <h4 className="text-xs font-bold text-slate-900">{je.eventName}</h4>
                    <span className="text-[11px] text-slate-500">Scheduled: {je.period}</span>
                  </div>
                </div>

                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800">
                  <CheckCircle2 className="w-3 h-3 mr-1" /> Balanced ($Debit == $Credit)
                </span>
              </div>

              <table className="min-w-full divide-y divide-slate-200 text-left text-xs">
                <thead className="bg-white text-slate-500 uppercase font-semibold">
                  <tr>
                    <th className="px-6 py-3">GL Account</th>
                    <th className="px-6 py-3">Description</th>
                    <th className="px-6 py-3 text-right">Debit ($)</th>
                    <th className="px-6 py-3 text-right">Credit ($)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-mono">
                  {je.lines.map((line: any, idx: number) => (
                    <tr key={idx} className="hover:bg-slate-50/50">
                      <td className="px-6 py-3 font-semibold text-slate-900">
                        {line.accountNumber} – {line.accountName}
                      </td>
                      <td className="px-6 py-3 text-slate-600 font-sans">{line.description}</td>
                      <td className="px-6 py-3 text-right font-bold text-slate-900">
                        {line.debit ? `$${line.debit.toLocaleString()}` : '—'}
                      </td>
                      <td className="px-6 py-3 text-right font-bold text-slate-900">
                        {line.credit ? `$${line.credit.toLocaleString()}` : '—'}
                      </td>
                    </tr>
                  ))}
                  <tr className="bg-slate-50/80 font-bold border-t border-slate-200">
                    <td colSpan={2} className="px-6 py-3 text-right font-sans uppercase text-slate-500">
                      Total
                    </td>
                    <td className="px-6 py-3 text-right text-slate-900">${je.totalDebit.toLocaleString()}</td>
                    <td className="px-6 py-3 text-right text-slate-900">${je.totalCredit.toLocaleString()}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          ))}
        </div>
      )}

      {/* SubTab 3: Executive Memo & Audit Notes */}
      {activeSubTab === 'fullMemo' && (
        <div className="bg-white p-8 rounded-xl border border-slate-200 shadow-sm space-y-6">
          <div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-bold uppercase tracking-wider text-slate-700">Executive Accounting Summary</h3>
              <button
                onClick={() => setIsEditing(!isEditing)}
                className="text-xs text-indigo-600 hover:text-indigo-800 font-semibold inline-flex items-center space-x-1"
              >
                <Edit3 className="w-3.5 h-3.5" />
                <span>{isEditing ? 'Done Editing' : 'Edit Summary'}</span>
              </button>
            </div>
            {isEditing ? (
              <textarea
                value={editedExecutiveSummary}
                onChange={(e) => setEditedExecutiveSummary(e.target.value)}
                rows={4}
                className="w-full text-xs p-3 border border-indigo-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 font-sans"
              />
            ) : (
              <p className="text-xs text-slate-600 leading-relaxed bg-slate-50 p-4 rounded-lg border border-slate-200">
                {editedExecutiveSummary || memo.executiveSummary}
              </p>
            )}
          </div>

          <div>
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-700 mb-2">Audit Conclusion & Notes</h3>
            <p className="text-xs text-slate-600 leading-relaxed bg-slate-50 p-4 rounded-lg border border-slate-200">
              {memo.conclusionAndDisclosures}
            </p>
          </div>

          <div className="border-t border-slate-200 pt-6 flex items-center justify-between text-xs text-slate-500">
            <div>
              <span>Prepared By: <strong className="text-slate-800">{memo.preparedBy}</strong></span>
            </div>
            <div>
              <span>Reviewed By: <strong className="text-slate-800">{memo.reviewedBy || 'Pending Final Review'}</strong></span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

