import React, { useState, useRef } from 'react';
import { Upload, FileCheck, AlertCircle, Loader2 } from 'lucide-react';

interface UploadZoneProps {
  onUploadSuccess: (doc: any) => void;
}

export const UploadZone: React.FC<UploadZoneProps> = ({ onUploadSuccess }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragging(true);
    } else if (e.type === 'dragleave') {
      setIsDragging(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = async (file: File) => {
    setError(null);

    // 1. Validation
    if (!file.name.toLowerCase().endsWith('.pdf') && file.type !== 'application/pdf') {
      setError('Invalid file format. Please upload a standard PDF document.');
      return;
    }

    if (file.size > 50 * 1024 * 1024) {
      setError('File size exceeds the 50MB limit.');
      return;
    }

    // 2. Upload
    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/documents/upload', {
        method: 'POST',
        headers: {
          // Provide dev token if available
          Authorization: `Bearer ${localStorage.getItem('dca_token') || ''}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to upload document.');
      }

      const data = await response.json();
      onUploadSuccess(data.document);
    } catch (err: any) {
      setError(err.message || 'An error occurred during upload.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-12 px-4">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Upload Document for Analysis</h2>
        <p className="mt-2 text-sm text-slate-600">
          Upload any contract, NDA, MSA, or commercial agreement in PDF format. Text and clause extraction will run automatically.
        </p>
      </div>

      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition ${
          isDragging
            ? 'border-indigo-600 bg-indigo-50/50'
            : 'border-slate-300 hover:border-indigo-400 bg-white shadow-sm'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handleFileInput}
          className="hidden"
        />

        <div className="flex flex-col items-center">
          {isUploading ? (
            <div className="flex flex-col items-center py-4">
              <Loader2 className="w-12 h-12 text-indigo-600 animate-spin mb-3" />
              <p className="text-sm font-semibold text-slate-800">Processing & Analyzing Document...</p>
              <p className="text-xs text-slate-500 mt-1">Extracting layout, clauses, and checking grounding citations</p>
            </div>
          ) : (
            <>
              <div className="w-14 h-14 rounded-full bg-indigo-50 flex items-center justify-center text-indigo-600 mb-4">
                <Upload className="w-7 h-7" />
              </div>
              <p className="text-base font-semibold text-slate-800">
                Drag and drop your contract PDF here, or <span className="text-indigo-600 underline">browse</span>
              </p>
              <p className="text-xs text-slate-500 mt-2">Supports PDF up to 50MB (scanned or native digital)</p>
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="mt-4 p-4 rounded-lg bg-red-50 border border-red-200 flex items-start space-x-3 text-red-700 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 bg-white rounded-lg border border-slate-200 shadow-sm flex items-start space-x-3">
          <FileCheck className="w-5 h-5 text-indigo-600 mt-0.5" />
          <div>
            <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">Layout Preservation</h4>
            <p className="text-xs text-slate-600 mt-1">Bounding boxes & tables are preserved for spatial reference.</p>
          </div>
        </div>
        <div className="p-4 bg-white rounded-lg border border-slate-200 shadow-sm flex items-start space-x-3">
          <FileCheck className="w-5 h-5 text-emerald-600 mt-0.5" />
          <div>
            <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">Hallucination Guard</h4>
            <p className="text-xs text-slate-600 mt-1">Every extracted clause is grounded against verbatim document quotes.</p>
          </div>
        </div>
        <div className="p-4 bg-white rounded-lg border border-slate-200 shadow-sm flex items-start space-x-3">
          <FileCheck className="w-5 h-5 text-amber-600 mt-0.5" />
          <div>
            <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">Human-in-the-Loop</h4>
            <p className="text-xs text-slate-600 mt-1">Complete audit trails for analyst adjustments and approvals.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

