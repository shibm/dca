import React from 'react';
import { FileText, BarChart3, UploadCloud, ShieldCheck } from 'lucide-react';

interface HeaderProps {
  activeTab: 'ma-diligence' | 'upload' | 'documents' | 'analytics';
  setActiveTab: (tab: 'ma-diligence' | 'upload' | 'documents' | 'analytics') => void;
}

export const Header: React.FC<HeaderProps> = ({ activeTab, setActiveTab }) => {
  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('ma-diligence')}>
            <div className="w-10 h-10 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold shadow-sm">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <span className="font-bold text-lg text-slate-900 tracking-tight">DCA</span>
              <span className="text-xs text-slate-500 block">Document & Contract Analysis</span>
            </div>
          </div>

          <nav className="flex space-x-2">
            <button
              onClick={() => setActiveTab('ma-diligence')}
              className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-semibold transition ${
                activeTab === 'ma-diligence'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-700 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <ShieldCheck className="w-4 h-4" />
              <span>M&A / SLA Diligence (P1)</span>
            </button>

            <button
              onClick={() => setActiveTab('upload')}
              className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition ${
                activeTab === 'upload'
                  ? 'bg-indigo-50 text-indigo-700 font-semibold'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <UploadCloud className="w-4 h-4" />
              <span>Upload Contract</span>
            </button>

            <button
              onClick={() => setActiveTab('documents')}
              className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition ${
                activeTab === 'documents'
                  ? 'bg-indigo-50 text-indigo-700 font-semibold'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <FileText className="w-4 h-4" />
              <span>HITL Review</span>
            </button>

            <button
              onClick={() => setActiveTab('analytics')}
              className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition ${
                activeTab === 'analytics'
                  ? 'bg-indigo-50 text-indigo-700 font-semibold'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <BarChart3 className="w-4 h-4" />
              <span>Stakeholder Reports</span>
            </button>
          </nav>
        </div>
      </div>
    </header>
  );
};

