import { Component, inject, signal } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';

import { AuthService } from '../core/auth.service';
import { OAuthService } from './oauth.service';
import { ErrorMessageComponent } from '../shared/error-message.component';
import { LoadingSpinnerComponent } from '../shared/loading-spinner.component';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterLink,
    HttpClientModule,
    ErrorMessageComponent,
    LoadingSpinnerComponent
  ],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'],
})
export class LoginComponent {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private oauthService = inject(OAuthService);
  private router = inject(Router);
  
  // Form state
  loginForm: FormGroup;
  
  // Component state
  isLoading = signal(false);
  errorMsg = signal('');
  
  constructor() {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }
  
  // Form controls getters
  get email() { return this.loginForm.get('email'); }
  get password() { return this.loginForm.get('password'); }
  
  onSubmit(): void {
    if (this.loginForm.invalid) return;
    
    this.isLoading.set(true);
    this.errorMsg.set('');
    
    const { email, password } = this.loginForm.value;
    
    this.authService.login(email, password).subscribe({
      next: success => {
        this.isLoading.set(false);
        if (success) {
          this.router.navigate(['/dashboard']);
        } else {
          this.errorMsg.set('Invalid email or password');
        }
      },
      error: error => {
        this.isLoading.set(false);
        this.errorMsg.set(error.error?.message || 'An error occurred during login');
      }
    });
  }
  
  loginWithGoogle(): void {
    this.oauthService.initiateGoogleLogin();
  }
  
  loginWithMicrosoft(): void {
    this.oauthService.initiateMicrosoftLogin();
  }
}
