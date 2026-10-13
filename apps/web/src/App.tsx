import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { UploadZone } from './components/UploadZone';
import { DocumentList } from './components/DocumentList';
import { ReviewSplitView } from './components/ReviewSplitView';
import { AnalyticsDashboard } from './components/AnalyticsDashboard';
import { DocumentItem, ExtractedField } from './types';

// Initial demo contracts for preview
const INITIAL_DEMO_DOCS: DocumentItem[] = [
  {
    id: 'demo-doc-1',
    file_name: 'Master_Services_Agreement_Acme_Apex.pdf',
    file_size_bytes: 42300,
    page_count: 2,
    document_type: 'msa',
    status: 'NEEDS_REVIEW',
    metadata: {
      overall_confidence: 0.913,
      flags: ['Risk [HIGH]: Unlimited Liability Clause'],
    },
    created_at: new Date().toISOString(),
  },
  {
    id: 'demo-doc-2',
    file_name: 'Mutual_NDA_CloudTech.pdf',
    file_size_bytes: 28400,
    page_count: 1,
    document_type: 'nda',
    status: 'APPROVED',
    metadata: {
      overall_confidence: 0.965,
      flags: [],
    },
    created_at: new Date(Date.now() - 86400000).toISOString(),
  },
];

const DEMO_EXTRACTIONS: Record<string, ExtractedField[]> = {
  'demo-doc-1': [
    {
      id: 'ext-1',
      field_key: 'title',
      field_label: 'Document Title',
      field_value: 'Master Services Agreement',
      field_category: 'general',
      data_type: 'string',
      confidence_score: 0.95,
      source_page: 1,
      source_quote: 'MASTER SERVICES AGREEMENT',
      is_corrected: false,
      validation_status: 'VALID',
    },
    {
      id: 'ext-2',
      field_key: 'party_1',
      field_label: 'Party #1 (Client)',
      field_value: 'Acme Global Technologies Inc.',
      field_category: 'parties',
      data_type: 'string',
      confidence_score: 0.95,
      source_page: 1,
      source_quote: 'Acme Global Technologies Inc., a Delaware corporation having its principal office at 100 Enterprise Way',
      source_bounding_box: { x0: 0.088, y0: 0.224, x1: 0.52, y1: 0.24, page: 1 },
      is_corrected: false,
      validation_status: 'VALID',
    },
    {
      id: 'ext-3',
      field_key: 'party_2',
      field_label: 'Party #2 (Vendor)',
      field_value: 'Apex Cloud Solutions LLC',
      field_category: 'parties',
      data_type: 'string',
      confidence_score: 0.95,
      source_page: 1,
      source_quote: 'Apex Cloud Solutions LLC, a California limited liability company',
      source_bounding_box: { x0: 0.088, y0: 0.252, x1: 0.49, y1: 0.268, page: 1 },
      is_corrected: false,
      validation_status: 'VALID',
    },
    {
      id: 'ext-4',
      field_key: 'effective_date',
      field_label: 'Effective Date',
      field_value: 'October 15, 2026',
      field_category: 'dates',
      data_type: 'date',
      confidence_score: 0.95,
      source_page: 1,
      source_quote: 'effective as of October 15, 2026',
      is_corrected: false,
      validation_status: 'VALID',
    },
    {
      id: 'ext-5',
      field_key: 'total_contract_value',
      field_label: 'Total Contract Value',
      field_value: 'USD 175,000.00',
      field_category: 'financial',
      data_type: 'currency',
      confidence_score: 0.95,
      source_page: 1,
      source_quote: 'total contract value of $175,000.00 USD for the initial phase',
      is_corrected: false,
      validation_status: 'VALID',
    },
    {
      id: 'ext-6',
      field_key: 'governing_law',
      field_label: 'Governing Law',
      field_value: 'State of Delaware',
      field_category: 'legal',
      data_type: 'string',
      confidence_score: 0.95,
      source_page: 2,
      source_quote: 'governed by and construed in accordance with the laws of the State of Delaware',
      is_corrected: false,
      validation_status: 'VALID',
    },
    {
      id: 'ext-7',
      field_key: 'risk_unlimited_liability',
      field_label: 'Risk: Unlimited Liability (HIGH)',
      field_value: 'Vendor assumes unlimited liability for direct regulatory penalties assessed by state authorities.',
      field_category: 'risk',
      data_type: 'string',
      confidence_score: 0.88,
      source_page: 2,
      source_quote: 'Vendor assumes unlimited liability for direct regulatory penalties',
      is_corrected: false,
      validation_status: 'WARNING',
    },
  ],
};

import { MADiligenceView } from './components/MADiligenceView';

import { PortfolioFinancialComparator } from './components/PortfolioFinancialComparator';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'ma-diligence' | 'financial-comparator' | 'upload' | 'documents' | 'analytics'>('financial-comparator');
  const [documents, setDocuments] = useState<DocumentItem[]>(INITIAL_DEMO_DOCS);
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);
  const [extractions, setExtractions] = useState<ExtractedField[]>(DEMO_EXTRACTIONS['demo-doc-1']);

  // Fetch real documents from BFF if available
  useEffect(() => {
    fetch('/api/documents')
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data?.documents && data.documents.length > 0) {
          setDocuments(data.documents);
        }
      })
      .catch(() => {
        // Fallback to demo items
      });
  }, []);

  const handleSelectDocument = async (id: string) => {
    setSelectedDocId(id);
    try {
      const res = await fetch(`/api/documents/${id}`);
      if (res.ok) {
        const data = await res.json();
        setExtractions(data.extractions || []);
      } else {
        setExtractions(DEMO_EXTRACTIONS[id] || DEMO_EXTRACTIONS['demo-doc-1']);
      }
    } catch {
      setExtractions(DEMO_EXTRACTIONS[id] || DEMO_EXTRACTIONS['demo-doc-1']);
    }
  };

  const handleFieldUpdate = async (fieldId: string, newValue: string, reason: string) => {
    try {
      await fetch(`/api/extractions/${fieldId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ value: newValue, reason }),
      });
    } catch {
      // Local fallback
    }

    setExtractions((prev) =>
      prev.map((f) =>
        f.id === fieldId
          ? { ...f, field_value: newValue, is_corrected: true, validation_status: 'VALID' }
          : f
      )
    );
  };

  const handleApprove = async (docId: string) => {
    try {
      await fetch(`/api/extractions/documents/${docId}/approve`, {
        method: 'POST',
      });
    } catch {
      // Local fallback
    }

    setDocuments((prev) =>
      prev.map((d) => (d.id === docId ? { ...d, status: 'APPROVED' } : d))
    );
    setSelectedDocId(null);
  };

  const handleUploadSuccess = (newDoc: DocumentItem) => {
    setDocuments((prev) => [newDoc, ...prev]);
    setActiveTab('documents');
  };

  const activeDoc = documents.find((d) => d.id === selectedDocId) || documents[0];

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Header activeTab={activeTab} setActiveTab={(tab) => {
        setSelectedDocId(null);
        setActiveTab(tab);
      }} />

      <main className="flex-1">
        {selectedDocId && activeDoc ? (
          <ReviewSplitView
            document={activeDoc}
            extractions={extractions}
            onBack={() => setSelectedDocId(null)}
            onFieldUpdate={handleFieldUpdate}
            onApprove={handleApprove}
          />
        ) : (
          <>
            {activeTab === 'financial-comparator' && <PortfolioFinancialComparator />}
            {activeTab === 'ma-diligence' && (
              <MADiligenceView onSelectContract={handleSelectDocument} />
            )}
            {activeTab === 'upload' && <UploadZone onUploadSuccess={handleUploadSuccess} />}
            {activeTab === 'documents' && (
              <DocumentList documents={documents} onSelectDocument={handleSelectDocument} />
            )}
            {activeTab === 'analytics' && <AnalyticsDashboard />}
          </>
        )}
      </main>
    </div>
  );
};

