import { Injectable, inject, signal, computed } from '@angular/core';
import { Observable, BehaviorSubject, switchMap, map, startWith, catchError, of, combineLatest } from 'rxjs';
import { toSignal, toObservable } from '@angular/core/rxjs-interop';
import { ApiService } from '../core/api.service';
import { 
  UrlModel, 
  UrlSubmission, 
  UrlBatchSubmission, 
  UrlSubmissionResponse, 
  UrlBatchSubmissionResponse,
  UrlStatus,
  ResourceState 
} from './url.model';

@Injectable({
  providedIn: 'root'
})
export class UrlService {
  private readonly apiService = inject(ApiService);
  
  // Refresh trigger for URL lists
  private readonly refreshTrigger$ = new BehaviorSubject<void>(undefined);
  
  // Current project ID signal for reactive URL fetching
  readonly currentProjectId = signal<string | null>(null);
  
  // Current status filter for URL lists
  readonly statusFilter = signal<UrlStatus | null>(null);
  
  // Convert signals to observables for reactive streams
  private readonly currentProjectId$ = toObservable(this.currentProjectId);
  private readonly statusFilter$ = toObservable(this.statusFilter);
  
  // Reactive URL list based on current project and filter
  private readonly urls$ = combineLatest([
    this.currentProjectId$,
    this.refreshTrigger$
  ]).pipe(
    switchMap(([projectId]) => {
      if (!projectId) {
        return of<ResourceState<UrlModel[]>>({ status: 'idle' });
      }
      
      return this.getUrlsInProject$(projectId, this.statusFilter()).pipe(
        map((data) => ({ status: 'success', data }) as const),
        startWith({ status: 'loading' } as const),
        catchError((error) => of({ status: 'error', error } as const))
      );
    })
  );
  
  readonly urlsState = toSignal(this.urls$, {
    initialValue: { status: 'idle' } as ResourceState<UrlModel[]>
  });
  
  readonly urls = computed(() => {
    const state = this.urlsState();
    return state?.status === 'success' ? (state.data as UrlModel[]) : [];
  });
  
  readonly isUrlsLoading = computed(() => {
    const state = this.urlsState();
    return state?.status === 'loading';
  });
  
  readonly urlsError = computed(() => {
    const state = this.urlsState();
    return state?.status === 'error' ? state.error : null;
  });
  
  // Filtered URLs based on status
  readonly filteredUrls = computed(() => {
    const urls = this.urls();
    const filter = this.statusFilter();
    return filter ? urls.filter((url: UrlModel) => url.status === filter) : urls;
  });

  /**
   * Submit a single URL to a project
   */
  submitSingleUrl$(projectId: string, urlData: UrlSubmission): Observable<UrlSubmissionResponse> {
    return this.apiService.post<UrlSubmissionResponse>(`projects/${projectId}/urls`, urlData);
  }

  /**
   * Submit multiple URLs to a project
   */
  submitMultipleUrls$(projectId: string, urlData: UrlBatchSubmission): Observable<UrlBatchSubmissionResponse> {
    return this.apiService.post<UrlBatchSubmissionResponse>(`projects/${projectId}/urls:batch`, urlData);
  }

  /**
   * Get all URLs in a project with optional status filter
   */
  getUrlsInProject$(projectId: string, status?: UrlStatus | null): Observable<UrlModel[]> {
    const params = status ? { status } : {};
    return this.apiService.get<UrlModel[]>(`projects/${projectId}/urls`, params);
  }

  /**
   * Get a specific URL's status and details
   */
  getUrlStatus$(projectId: string, urlId: string): Observable<UrlModel> {
    return this.apiService.get<UrlModel>(`projects/${projectId}/urls/${urlId}`);
  }

  /**
   * Set the current project ID to fetch URLs for
   */
  setCurrentProject(projectId: string | null): void {
    this.currentProjectId.set(projectId);
  }

  /**
   * Set the status filter for URL lists
   */
  setStatusFilter(status: UrlStatus | null): void {
    this.statusFilter.set(status);
  }

  /**
   * Refresh the URL list for the current project
   */
  refreshUrls(): void {
    this.refreshTrigger$.next();
  }

  /**
   * Delete a specific URL by ID
   */
  deleteUrl$(projectId: string, urlId: string): Observable<void> {
    return this.apiService.delete<void>(`projects/${projectId}/urls/${urlId}`);
  }

  /**
   * Get URL count by status for the current project
   */
  readonly urlCountByStatus = computed(() => {
    const urls = this.urls();
    return urls.reduce((counts: Record<UrlStatus, number>, url: UrlModel) => {
      counts[url.status] = (counts[url.status] || 0) + 1;
      return counts;
    }, {} as Record<UrlStatus, number>);
  });
}
