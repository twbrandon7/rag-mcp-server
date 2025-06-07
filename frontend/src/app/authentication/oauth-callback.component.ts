import { Component, inject, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { LoadingSpinnerComponent } from '../shared/loading-spinner.component';
import { ErrorMessageComponent } from '../shared/error-message.component';
import { OAuthService } from './oauth.service';

@Component({
  selector: 'app-oauth-callback',
  standalone: true,
  imports: [
    CommonModule,
    LoadingSpinnerComponent,
    ErrorMessageComponent
  ],
  template: `
    <div class="oauth-callback-container">
      <h2>Processing Login</h2>
      
      <app-loading-spinner *ngIf="!error"></app-loading-spinner>
      
      <div class="error-container" *ngIf="error">
        <app-error-message [message]="error"></app-error-message>
        <button class="btn-primary" (click)="navigateToLogin()">
          Return to Login
        </button>
      </div>
    </div>
  `,
  styles: `
    .oauth-callback-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      width: 100%;
      padding: 2rem;
      text-align: center;
    }
    
    h2 {
      margin-bottom: 2rem;
      color: #333;
    }
    
    .error-container {
      width: 100%;
      max-width: 400px;
    }
    
    button {
      cursor: pointer;
      font-size: 1rem;
      border-radius: 4px;
      transition: background-color 0.2s;
      padding: 0.75rem 1rem;
      border: none;
      width: 100%;
      margin-top: 1rem;
    }
    
    .btn-primary {
      background-color: #0066cc;
      color: white;
      font-weight: 500;
    }
    
    .btn-primary:hover {
      background-color: #0055b3;
    }
  `
})
export class OAuthCallbackComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private oauthService = inject(OAuthService);
  
  protected error: string = '';
  
  ngOnInit(): void {
    const code = this.route.snapshot.queryParamMap.get('code');
    const error = this.route.snapshot.queryParamMap.get('error');
    const provider = this.route.snapshot.paramMap.get('provider');
    
    if (error) {
      this.error = `Authentication error: ${error}`;
      return;
    }
    
    if (!code) {
      this.error = 'No authentication code received';
      return;
    }
    
    if (!provider) {
      this.error = 'Unknown authentication provider';
      return;
    }
    
    this.handleOAuthCallback(provider, code);
  }
  
  private handleOAuthCallback(provider: string, code: string): void {
    // Pass the code as a fragment to the handleCallback method
    // This simulates the fragment that would be received in a real OAuth flow
    const fragment = `access_token=${code}&state=${provider}`;
    
    this.oauthService.handleCallback(fragment).subscribe({
      next: (success) => {
        if (success) {
          this.router.navigate(['/dashboard']);
        } else {
          this.error = `Error processing ${provider} login. Please try again.`;
        }
      },
      error: (error: Error) => {
        this.error = `Error processing ${provider} login. Please try again.`;
        console.error(`${provider} callback error:`, error);
      }
    });
  }
  
  navigateToLogin(): void {
    this.router.navigate(['/auth/login']);
  }
}
