import { Component, input } from '@angular/core';

@Component({
  selector: 'app-error-message',
  standalone: true,
  template: `
    <div class="error-container" *ngIf="message()">
      {{ message() }}
    </div>
  `,
  styles: `
    .error-container {
      padding: 0.75rem 1rem;
      background-color: #ffebee;
      color: #c62828;
      border-left: 4px solid #c62828;
      margin-bottom: 1rem;
      border-radius: 4px;
      font-size: 0.875rem;
    }
  `
})
export class ErrorMessageComponent {
  readonly message = input<string>('');
}
