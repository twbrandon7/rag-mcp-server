import { Component, input, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UrlStatus } from '../url.model';

@Component({
  selector: 'app-url-status',
  imports: [CommonModule],
  templateUrl: './url-status.component.html',
  styleUrl: './url-status.component.scss'
})
export class UrlStatusComponent {
  readonly status = input.required<UrlStatus>();

  readonly statusConfig = computed(() => {
    const status = this.status();
    
    const configs: Record<UrlStatus, { label: string; class: string; icon: string }> = {
      pending: { label: 'Pending', class: 'status-pending', icon: '⏳' },
      crawling: { label: 'Crawling', class: 'status-crawling', icon: '🕷️' },
      encoding: { label: 'Encoding', class: 'status-encoding', icon: '⚙️' },
      stored: { label: 'Stored', class: 'status-stored', icon: '✅' },
      failed: { label: 'Failed', class: 'status-failed', icon: '❌' }
    };
    
    return configs[status];
  });
}
