export interface ExtractedField {
  id: string;
  field_key: string;
  field_label: string;
  field_value: string;
  field_category: string;
  data_type: string;
  confidence_score: number;
  source_page?: number;
  source_quote?: string;
  source_bounding_box?: {
    x0: number;
    y0: number;
    x1: number;
    y1: number;
    page: number;
  };
  is_corrected: boolean;
  validation_status: 'VALID' | 'WARNING' | 'INVALID' | 'NEEDS_VERIFICATION';
}

export interface DocumentItem {
  id: string;
  file_name: string;
  file_size_bytes: number;
  page_count: number;
  document_type: string;
  status: 'UPLOADED' | 'PROCESSING' | 'NEEDS_REVIEW' | 'APPROVED' | 'FAILED';
  metadata?: {
    overall_confidence?: number;
    processing_time_ms?: number;
    flags?: string[];
  };
  created_at: string;
  uploaded_by?: string;
  total_extracted_fields?: number;
}

