import { Component, inject, input, computed, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UrlService } from '../url.service';
import { UrlStatusComponent } from '../url-status/url-status.component';
import { UrlModel, UrlStatus } from '../url.model';
import { Router } from '@angular/router';
import { take } from 'rxjs';

@Component({
  selector: 'app-url-list',
  imports: [CommonModule, UrlStatusComponent],
  templateUrl: './url-list.component.html',
  styleUrl: './url-list.component.scss'
})
export class UrlListComponent {
  private readonly urlService = inject(UrlService);
  private router = inject(Router);

  // Inputs
  readonly projectId = input.required<string>();

  // Inject URL service state
  readonly urls = this.urlService.filteredUrls;
  readonly isLoading = this.urlService.isUrlsLoading;
  readonly error = this.urlService.urlsError;
  readonly urlCountByStatus = this.urlService.urlCountByStatus;
  readonly currentFilter = this.urlService.statusFilter;

  // Available status filters
  readonly statusFilters: (UrlStatus | null)[] = [null, 'pending', 'crawling', 'encoding', 'stored', 'failed'];

  // Computed properties for display
  readonly hasUrls = computed(() => this.urls().length > 0);
  readonly totalUrlCount = computed(() => {
    const counts = this.urlCountByStatus();
    return Object.values(counts).reduce((sum, count) => sum + count, 0);
  });

  // Url deletion

  constructor() {
    // Watch for project ID changes and update the service
    effect(() => {
      const projectId = this.projectId();
      if (projectId) {
        this.urlService.setCurrentProject(projectId);
      }
    });
  }

  public refreshUrls(): void {
    this.urlService.refreshUrls();
  }

  protected onFilterChange(status: UrlStatus | null): void {
    this.urlService.setStatusFilter(status);
  }

  protected onRefresh(): void {
    this.urlService.refreshUrls();
  }

  protected onDeleteUrl(urlId: string): void {
    this.urlService.deleteUrl$(this.projectId(), urlId).pipe(take(1)).subscribe({
      next: () => {
        // Handle successful deletion (e.g., refresh the URL list)
        this.refreshUrls();
      },
      error: (err) => {
        // Handle error (e.g., show a notification)
        console.error('Error deleting URL:', err);
      }
    });
  }

  protected getStatusDisplayName(status: UrlStatus | null): string {
    if (!status) return 'All';

    const statusMap: Record<UrlStatus, string> = {
      pending: 'Pending',
      crawling: 'Crawling',
      encoding: 'Encoding',
      stored: 'Stored',
      failed: 'Failed'
    };

    return statusMap[status];
  }

  protected getStatusClass(status: UrlStatus): string {
    const statusClasses: Record<UrlStatus, string> = {
      pending: 'status-pending',
      crawling: 'status-crawling',
      encoding: 'status-encoding',
      stored: 'status-stored',
      failed: 'status-failed'
    };

    return statusClasses[status];
  }

  protected formatDate(dateString: string): string {
    return new Date(dateString).toLocaleString();
  }

  protected truncateUrl(url: string, maxLength: number = 50): string {
    return url.length > maxLength ? url.substring(0, maxLength) + '...' : url;
  }
}
