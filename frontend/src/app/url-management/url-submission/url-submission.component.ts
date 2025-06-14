import { Component, inject, input, output, signal, computed, OnDestroy, effect } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { switchMap, catchError, of, EMPTY, startWith, map, finalize, tap, filter } from 'rxjs';
import { toSignal, toObservable } from '@angular/core/rxjs-interop';
import { UrlService } from '../url.service';
import { UrlSubmission, UrlBatchSubmission, UrlSubmissionResponse, UrlBatchSubmissionResponse } from '../url.model';

@Component({
  selector: 'app-url-submission',
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './url-submission.component.html',
  styleUrl: './url-submission.component.scss'
})
export class UrlSubmissionComponent implements OnDestroy {
  private readonly fb = inject(FormBuilder);
  private readonly urlService = inject(UrlService);

  // Inputs
  readonly projectId = input.required<string>();

  // Outputs
  readonly urlSubmitted = output<UrlSubmissionResponse>();
  readonly batchSubmitted = output<UrlBatchSubmissionResponse>();
  readonly submissionError = output<string>();

  // Form controls
  readonly singleUrlForm: FormGroup = this.fb.group({
    url: ['', [Validators.required, Validators.pattern(/^https?:\/\/.+/)]]
  });
  readonly multipleUrlsForm: FormGroup = this.fb.group({
    urls: ['', [Validators.required]]
  });

  // Form status signals
  readonly singleFormValid = toSignal(this.singleUrlForm.statusChanges.pipe(
    startWith(this.singleUrlForm.status),
    map(() => this.singleUrlForm.valid)
  ), { initialValue: this.singleUrlForm.valid });
  
  readonly multipleFormValid = toSignal(this.multipleUrlsForm.statusChanges.pipe(
    startWith(this.multipleUrlsForm.status),
    map(() => this.multipleUrlsForm.valid)
  ), { initialValue: this.multipleUrlsForm.valid });

  // UI state
  readonly submissionMode = signal<'single' | 'multiple'>('single');
  readonly isSubmitting = signal(false);
  readonly submissionResult = signal<string | null>(null);
  readonly submissionSuccess = signal(false);

  // Submission triggers
  private readonly singleUrlSubmission = signal<{ projectId: string; url: string } | null>(null);
  private readonly multipleUrlsSubmission = signal<{ projectId: string; urls: string[] } | null>(null);

  // Form value change signals to clear messages reactively
  readonly singleUrl = toSignal(this.singleUrlForm.get('url')?.valueChanges || EMPTY, { initialValue: '' });
  readonly multipleUrls = toSignal(this.multipleUrlsForm.get('urls')?.valueChanges || EMPTY, { initialValue: '' });

  private readonly _singleUrlChangeSignalEffect = effect(() => {
    if (!Boolean(this.singleUrl()) || this.singleUrl().trim() === '') return;
    this.submissionResult.set(null);
    this.submissionSuccess.set(false);
  });

  private readonly _multipleUrlsChangeSignalEffect = effect(() => {
    if (!Boolean(this.multipleUrls()) || this.multipleUrls().trim() === '') return;
    this.submissionResult.set(null);
    this.submissionSuccess.set(false);
  });

  // Submission logics
  private readonly singleUrlSubmission$ = toObservable(this.singleUrlSubmission).pipe(
    filter(submission => submission !== null),
    switchMap(submission => this.urlService.submitSingleUrl$(
      submission.projectId,
      {
        original_url: submission.url
      } as UrlSubmission
    ).pipe(
      tap(response => {
        this.submissionResult.set(`URL submitted successfully`);
        this.submissionSuccess.set(true);
        this.urlSubmitted.emit(response);
        this.singleUrlForm.reset();
      }),
      catchError(error => {
        const errorMessage = this.getErrorMessage(error);
        this.submissionError.emit(errorMessage);
        this.submissionSuccess.set(false);
        this.submissionResult.set(errorMessage);
        return of(null); // Continue the stream
      }),
      finalize(() => this.isSubmitting.set(false))
    )),
  );

  private readonly multipleUrlsSubmission$ = toObservable(this.multipleUrlsSubmission).pipe(
    filter(submission => submission !== null),
    switchMap(submission => this.urlService.submitMultipleUrls$(
      submission.projectId,
      {
        urls: submission.urls
      } as UrlBatchSubmission
    ).pipe(
      tap(response => {
        this.submissionResult.set(`Batch submitted successfully. ${response.submitted_urls.length} URLs submitted. ${response.duplicate_urls.length} duplicates found.`);
        this.submissionSuccess.set(true);
        this.batchSubmitted.emit(response);
        this.multipleUrlsForm.reset();
      }),
      catchError(error => {
        const errorMessage = this.getErrorMessage(error);
        this.submissionError.emit(errorMessage);
        this.submissionSuccess.set(false);
        this.submissionResult.set(errorMessage)
        return of(null); // Continue the stream
      }),
      finalize(() => this.isSubmitting.set(false))
    )),
  );

  private singleUrlSubmissionSubscription = this.singleUrlSubmission$.subscribe();
  private multipleUrlsSubmissionSubscription = this.multipleUrlsSubmission$.subscribe();

  ngOnDestroy(): void {
    this.singleUrlSubmissionSubscription.unsubscribe();
    this.multipleUrlsSubmissionSubscription.unsubscribe();
  }

  private getErrorMessage(error: any): string {
    if (error?.status === 409) {
      return 'URL already exists in this project';
    }
    if (error?.status === 400) {
      return 'Invalid URL format';
    }
    if (error?.status === 404) {
      return 'Project not found';
    }
    return error?.message || 'An error occurred while submitting URLs';
  }

  onSubmitSingleUrl() {
    const url = this.singleUrlForm.get('url')?.value.trim();
    if (!url) {
      this.submissionError.emit('URL cannot be empty');
      return;
    }
    this.singleUrlSubmission.set({ projectId: this.projectId(), url });
  }

  onSubmitMultipleUrls() {
    const urlsInput: string = this.multipleUrlsForm.get('urls')?.value.trim();
    if (!urlsInput) {
      this.submissionError.emit('URLs cannot be empty');
      return;
    }
    
    // Split by new lines and filter out empty lines
    const urls = urlsInput.split('\n').map(url => url.trim()).filter(url => url);
    
    if (urls.length === 0) {
      this.submissionError.emit('No valid URLs provided');
      return;
    }

    this.multipleUrlsSubmission.set({ projectId: this.projectId(), urls });
  }

  protected toggleSubmissionMode(): void {
    const currentMode = this.submissionMode();
    this.submissionMode.set(currentMode === 'single' ? 'multiple' : 'single');

    // Reset forms when switching modes
    this.singleUrlForm.reset();
    this.multipleUrlsForm.reset();
    
    // Clear messages when switching modes
    this.submissionResult.set(null);
    this.submissionSuccess.set(false);
  }

  protected switchToSingleMode(): void {
    if (this.submissionMode() !== 'single') {
      this.submissionMode.set('single');
      this.clearFormsAndMessages();
    }
  }

  protected switchToMultipleMode(): void {
    if (this.submissionMode() !== 'multiple') {
      this.submissionMode.set('multiple');
      this.clearFormsAndMessages();
    }
  }

  private clearFormsAndMessages(): void {
    this.singleUrlForm.reset();
    this.multipleUrlsForm.reset();
    this.submissionResult.set(null);
    this.submissionSuccess.set(false);
  }

  // Computed properties for template
  readonly isSingleMode = computed(() => this.submissionMode() === 'single');
  readonly isMultipleMode = computed(() => this.submissionMode() === 'multiple');
  readonly canSubmitSingle = computed(() => this.singleFormValid() && !this.isSubmitting());
  readonly canSubmitMultiple = computed(() => this.multipleFormValid() && !this.isSubmitting());
}
