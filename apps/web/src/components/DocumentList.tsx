import React from 'react';
import { FileText, Clock, CheckCircle2, AlertTriangle, ArrowRight } from 'lucide-react';
import { DocumentItem } from '../types';

interface DocumentListProps {
  documents: DocumentItem[];
  onSelectDocument: (id: string) => void;
}

export const DocumentList: React.FC<DocumentListProps> = ({ documents, onSelectDocument }) => {
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'APPROVED':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
            <CheckCircle2 className="w-3 h-3 mr-1" /> Approved
          </span>
        );
      case 'NEEDS_REVIEW':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800">
            <AlertTriangle className="w-3 h-3 mr-1" /> Needs Review
          </span>
        );
      case 'PROCESSING':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            <Clock className="w-3 h-3 mr-1 animate-spin" /> Processing
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-800">
            {status}
          </span>
        );
    }
  };

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div className="sm:flex sm:items-center sm:justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Contracts & Document Repository</h2>
          <p className="mt-1 text-sm text-slate-500">
            Review parsed contracts, verify extracted fields, and finalize stakeholder approvals.
          </p>
        </div>
      </div>

      {documents.length === 0 ? (
        <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
          <FileText className="w-12 h-12 text-slate-400 mx-auto mb-3" />
          <p className="text-base font-medium text-slate-700">No documents uploaded yet</p>
          <p className="text-xs text-slate-500 mt-1">Upload a PDF to initiate automated extraction.</p>
        </div>
      ) : (
        <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
          <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
            <thead className="bg-slate-50 text-slate-500 uppercase text-xs font-semibold">
              <tr>
                <th className="px-6 py-3.5">Document</th>
                <th className="px-6 py-3.5">Type</th>
                <th className="px-6 py-3.5">Status</th>
                <th className="px-6 py-3.5">Confidence</th>
                <th className="px-6 py-3.5">Date</th>
                <th className="px-6 py-3.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {documents.map((doc) => {
                const conf = doc.metadata?.overall_confidence;
                return (
                  <tr key={doc.id} className="hover:bg-slate-50 transition cursor-pointer" onClick={() => onSelectDocument(doc.id)}>
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-3">
                        <FileText className="w-5 h-5 text-indigo-600 flex-shrink-0" />
                        <div>
                          <div className="font-medium text-slate-900">{doc.file_name}</div>
                          <div className="text-xs text-slate-500">{(doc.file_size_bytes / 1024).toFixed(1)} KB • {doc.page_count || 1} pages</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="uppercase text-xs font-semibold px-2 py-1 bg-slate-100 rounded text-slate-700">
                        {doc.document_type || 'Contract'}
                      </span>
                    </td>
                    <td className="px-6 py-4">{getStatusBadge(doc.status)}</td>
                    <td className="px-6 py-4">
                      {conf !== undefined ? (
                        <div className="flex items-center space-x-2">
                          <div className="w-16 bg-slate-200 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full ${
                                conf >= 0.85 ? 'bg-emerald-500' : conf >= 0.70 ? 'bg-amber-500' : 'bg-red-500'
                              }`}
                              style={{ width: `${conf * 100}%` }}
                            />
                          </div>
                          <span className="text-xs font-medium text-slate-700">{(conf * 100).toFixed(0)}%</span>
                        </div>
                      ) : (
                        <span className="text-xs text-slate-400">N/A</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-500">
                      {new Date(doc.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectDocument(doc.id);
                        }}
                        className="inline-flex items-center text-xs font-semibold text-indigo-600 hover:text-indigo-800"
                      >
                        Review <ArrowRight className="w-3.5 h-3.5 ml-1" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

