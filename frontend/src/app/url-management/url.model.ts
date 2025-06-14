export type UrlStatus = 'pending' | 'crawling' | 'encoding' | 'stored' | 'failed';

export interface UrlModel {
  url_id: string;
  project_id: string;
  original_url: string;
  status: UrlStatus;
  failure_reason: string | null;
  submitted_at: string;
  last_updated_at: string;
}

export interface UrlSubmission {
  original_url: string;
}

export interface UrlBatchSubmission {
  urls: string[];
}

export interface UrlSubmissionResponse {
  url_id: string;
  project_id: string;
  original_url: string;
  status: UrlStatus;
  failure_reason: string | null;
  submitted_at: string;
  last_updated_at: string;
}

export interface UrlBatchSubmissionResponse {
  submitted_urls: UrlSubmissionResponse[];
  duplicate_urls: UrlSubmissionResponse[];
}

export interface UrlDuplicateResponse {
  message: string;
  existing_url: UrlSubmissionResponse;
}

export type ResourceState<T> = 
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: any }
  | { status: 'idle' };
