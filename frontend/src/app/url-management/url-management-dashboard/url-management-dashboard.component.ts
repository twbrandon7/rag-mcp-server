import { Component, inject, signal, OnInit, viewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { UrlSubmissionComponent } from '../url-submission/url-submission.component';
import { UrlListComponent } from '../url-list/url-list.component';

@Component({
  selector: 'app-url-management-dashboard',
  imports: [CommonModule, UrlSubmissionComponent, UrlListComponent],
  templateUrl: './url-management-dashboard.component.html',
  styleUrl: './url-management-dashboard.component.scss'
})
export class UrlManagementDashboardComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly appUrlList = viewChild(UrlListComponent);

  readonly projectId = signal<string>('');

  ngOnInit(): void {
    // Get project ID from parent route params
    const projectIdParam = this.route.parent?.snapshot.paramMap.get('id');
    if (projectIdParam) {
      this.projectId.set(projectIdParam);
    }
  }

  protected onUrlSubmitted(): void {
    this.appUrlList()?.refreshUrls();
  }

  protected onBatchSubmitted(): void {
    this.appUrlList()?.refreshUrls();
  }

  protected onSubmissionError(error: string): void {
    console.error('URL submission error:', error);
  }
}
