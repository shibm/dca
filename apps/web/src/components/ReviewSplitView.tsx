import React, { useState } from 'react';
import { ArrowLeft, Check, CheckCircle2, AlertCircle, Sparkles, Edit3 } from 'lucide-react';
import { DocumentItem, ExtractedField } from '../types';

interface ReviewSplitViewProps {
  document: DocumentItem;
  extractions: ExtractedField[];
  onBack: () => void;
  onFieldUpdate: (fieldId: string, newValue: string, reason: string) => Promise<void>;
  onApprove: (docId: string) => Promise<void>;
}

export const ReviewSplitView: React.FC<ReviewSplitViewProps> = ({
  document,
  extractions,
  onBack,
  onFieldUpdate,
  onApprove,
}) => {
  const [selectedField, setSelectedField] = useState<ExtractedField | null>(
    extractions.length > 0 ? extractions[0] : null
  );
  const [editingFieldId, setEditingFieldId] = useState<string | null>(null);
  const [editValue, setEditValue] = useState<string>('');
  const [editReason, setEditReason] = useState<string>('');
  const [isSaving, setIsSaving] = useState(false);
  const [isApproving, setIsApproving] = useState(false);

  const startEdit = (field: ExtractedField) => {
    setEditingFieldId(field.id);
    setEditValue(field.field_value || '');
    setEditReason('');
    setSelectedField(field);
  };

  const handleSaveCorrection = async (fieldId: string) => {
    setIsSaving(true);
    try {
      await onFieldUpdate(fieldId, editValue, editReason);
      setEditingFieldId(null);
    } finally {
      setIsSaving(false);
    }
  };

  const handleApprove = async () => {
    setIsApproving(true);
    try {
      await onApprove(document.id);
    } finally {
      setIsApproving(false);
    }
  };

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col bg-slate-100">
      {/* Top action bar */}
      <div className="bg-white border-b border-slate-200 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={onBack}
            className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600 transition"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <h2 className="text-base font-bold text-slate-900">{document.file_name}</h2>
            <div className="flex items-center space-x-2 text-xs text-slate-500">
              <span className="uppercase font-semibold">{document.document_type || 'Contract'}</span>
              <span>•</span>
              <span>Status: <strong className="text-slate-800">{document.status}</strong></span>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleApprove}
            disabled={isApproving || document.status === 'APPROVED'}
            className="inline-flex items-center space-x-2 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold shadow-sm transition disabled:opacity-50"
          >
            <Check className="w-4 h-4" />
            <span>{document.status === 'APPROVED' ? 'Approved' : 'Approve & Finalize'}</span>
          </button>
        </div>
      </div>

      {/* Main split-screen */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left: Document View & Grounding Citation */}
        <div className="w-1/2 p-6 overflow-y-auto border-r border-slate-200 flex flex-col">
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex-1 flex flex-col">
            <div className="flex items-center justify-between border-b border-slate-200 pb-3 mb-4">
              <span className="text-xs font-bold uppercase text-slate-500 tracking-wider">
                Document Grounding Context
              </span>
              {selectedField?.source_page && (
                <span className="text-xs font-medium bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded">
                  Page {selectedField.source_page}
                </span>
              )}
            </div>

            {selectedField?.source_quote ? (
              <div className="p-4 rounded-lg bg-indigo-50/50 border border-indigo-200 mb-4">
                <div className="flex items-center space-x-2 text-indigo-700 font-semibold text-xs mb-1">
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Verbatim Document Citation</span>
                </div>
                <blockquote className="text-sm italic text-slate-800">
                  "{selectedField.source_quote}"
                </blockquote>
                {selectedField.source_bounding_box && (
                  <p className="text-[11px] text-slate-400 mt-2">
                    Spatial Coordinates: [x: {selectedField.source_bounding_box.x0}, y: {selectedField.source_bounding_box.y0}]
                  </p>
                )}
              </div>
            ) : (
              <div className="p-4 rounded-lg bg-slate-50 border border-slate-200 text-slate-500 text-xs italic mb-4">
                Select an extracted field on the right to inspect its grounding quote and page citation.
              </div>
            )}

            <div className="flex-1 bg-slate-50 rounded-lg p-6 border border-slate-200 overflow-y-auto font-mono text-xs text-slate-700 leading-relaxed">
              <div className="text-center text-slate-400 mb-4 font-sans text-xs">
                [ Interactive PDF Viewer Canvas ]
              </div>
              <p className="mb-3 font-bold text-slate-900">MASTER SERVICES AGREEMENT</p>
              <p className="mb-2">This Master Services Agreement is made effective as of October 15, 2026 by and between Acme Global Technologies Inc. ("Client") and Apex Cloud Solutions LLC ("Vendor").</p>
              <p className="mb-2">Total contract value is $175,000.00 USD. Client shall pay within Net 30 days upon invoice receipt.</p>
              <p className="mb-2">Governed by the laws of the State of Delaware.</p>
            </div>
          </div>
        </div>

        {/* Right: Extracted Fields & HITL Form */}
        <div className="w-1/2 p-6 overflow-y-auto">
          <div className="space-y-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-bold uppercase tracking-wider text-slate-700">
                Extracted Entities & Clauses ({extractions.length})
              </h3>
              <span className="text-xs text-slate-500">Click field to inspect citation</span>
            </div>

            {extractions.map((field) => {
              const isSelected = selectedField?.id === field.id;
              const isEditing = editingFieldId === field.id;

              return (
                <div
                  key={field.id}
                  onClick={() => setSelectedField(field)}
                  className={`bg-white rounded-xl border p-4 transition shadow-sm ${
                    isSelected ? 'border-indigo-500 ring-2 ring-indigo-100' : 'border-slate-200 hover:border-slate-300'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-slate-700 uppercase">{field.field_label}</span>
                    <div className="flex items-center space-x-2">
                      <span
                        className={`text-[11px] font-bold px-2 py-0.5 rounded-full ${
                          field.confidence_score >= 0.90
                            ? 'bg-emerald-100 text-emerald-800'
                            : field.confidence_score >= 0.70
                            ? 'bg-amber-100 text-amber-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {(field.confidence_score * 100).toFixed(0)}% Conf
                      </span>
                      {field.is_corrected && (
                        <span className="text-[11px] font-medium bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full">
                          Corrected
                        </span>
                      )}
                    </div>
                  </div>

                  {isEditing ? (
                    <div className="space-y-3 mt-2" onClick={(e) => e.stopPropagation()}>
                      <input
                        type="text"
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                        className="w-full text-sm px-3 py-2 border border-indigo-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
                        placeholder="Correct value..."
                      />
                      <input
                        type="text"
                        value={editReason}
                        onChange={(e) => setEditReason(e.target.value)}
                        className="w-full text-xs px-3 py-1.5 border border-slate-200 rounded-lg text-slate-600 focus:outline-none focus:ring-1 focus:ring-indigo-400"
                        placeholder="Correction reason (e.g. OCR typo / legal review)..."
                      />
                      <div className="flex justify-end space-x-2">
                        <button
                          onClick={() => setEditingFieldId(null)}
                          className="px-3 py-1 text-xs text-slate-600 hover:text-slate-800"
                        >
                          Cancel
                        </button>
                        <button
                          onClick={() => handleSaveCorrection(field.id)}
                          disabled={isSaving}
                          className="px-3 py-1 bg-indigo-600 hover:bg-indigo-700 text-white rounded text-xs font-semibold"
                        >
                          {isSaving ? 'Saving...' : 'Save Correction'}
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-center justify-between">
                      <div className="text-sm font-semibold text-slate-900 break-words max-w-[80%]">
                        {field.field_value || <span className="text-slate-400 italic">None detected</span>}
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          startEdit(field);
                        }}
                        className="p-1 rounded text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 transition"
                      >
                        <Edit3 className="w-4 h-4" />
                      </button>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

