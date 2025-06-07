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
  selector: 'app-register',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterLink,
    HttpClientModule,
    ErrorMessageComponent,
    LoadingSpinnerComponent
  ],
  template: `
    <div class="register-container">
      <h2>Create Account</h2>
      <app-error-message [message]="errorMsg()"></app-error-message>
      
      <form [formGroup]="registerForm" (ngSubmit)="onSubmit()" *ngIf="!isLoading()">
        <div class="form-group">
          <label for="email">Email</label>
          <input
            type="email"
            id="email"
            formControlName="email"
            placeholder="Enter your email"
            autocomplete="email"
          />
          <div class="error-text" *ngIf="email?.invalid && (email?.dirty || email?.touched)">
            <span *ngIf="email?.errors?.['required']">Email is required</span>
            <span *ngIf="email?.errors?.['email']">Please enter a valid email</span>
          </div>
        </div>
        
        <div class="form-group">
          <label for="password">Password</label>
          <input
            type="password"
            id="password"
            formControlName="password"
            placeholder="Create a password"
            autocomplete="new-password"
          />
          <div class="error-text" *ngIf="password?.invalid && (password?.dirty || password?.touched)">
            <span *ngIf="password?.errors?.['required']">Password is required</span>
            <span *ngIf="password?.errors?.['minlength']">Password must be at least 6 characters</span>
          </div>
        </div>
        
        <div class="form-group">
          <label for="confirmPassword">Confirm Password</label>
          <input
            type="password"
            id="confirmPassword"
            formControlName="confirmPassword"
            placeholder="Confirm your password"
            autocomplete="new-password"
          />
          <div class="error-text" *ngIf="confirmPassword?.invalid && (confirmPassword?.dirty || confirmPassword?.touched)">
            <span *ngIf="confirmPassword?.errors?.['required']">Please confirm your password</span>
          </div>
          <div class="error-text" *ngIf="registerForm.errors?.['passwordMismatch'] && (confirmPassword?.dirty || confirmPassword?.touched)">
            Passwords do not match
          </div>
        </div>
        
        <button type="submit" class="btn-primary" [disabled]="registerForm.invalid">
          Create Account
        </button>
      </form>
      
      <app-loading-spinner *ngIf="isLoading()"></app-loading-spinner>
      
      <div class="social-login">
        <p>Or sign up with</p>
        <div class="social-buttons">
          <button type="button" class="btn-google" (click)="signUpWithGoogle()">
            Google
          </button>
          <button type="button" class="btn-microsoft" (click)="signUpWithMicrosoft()">
            Microsoft
          </button>
        </div>
      </div>
      
      <div class="login-link">
        <p>Already have an account? <a routerLink="/auth/login">Sign In</a></p>
      </div>
    </div>
  `,
  styles: `
    .register-container {
      width: 100%;
    }
    
    h2 {
      text-align: center;
      margin-bottom: 1.5rem;
      color: #333;
    }
    
    .form-group {
      margin-bottom: 1.25rem;
    }
    
    label {
      display: block;
      margin-bottom: 0.5rem;
      font-weight: 500;
      color: #555;
    }
    
    input {
      width: 100%;
      padding: 0.75rem;
      border: 1px solid #ddd;
      border-radius: 4px;
      font-size: 1rem;
    }
    
    input:focus {
      outline: none;
      border-color: #0066cc;
      box-shadow: 0 0 0 2px rgba(0, 102, 204, 0.2);
    }
    
    .error-text {
      color: #d32f2f;
      font-size: 0.85rem;
      margin-top: 0.5rem;
    }
    
    button {
      cursor: pointer;
      font-size: 1rem;
      border-radius: 4px;
      transition: background-color 0.2s;
      padding: 0.75rem 1rem;
      border: none;
      width: 100%;
    }
    
    .btn-primary {
      background-color: #0066cc;
      color: white;
      font-weight: 500;
    }
    
    .btn-primary:hover {
      background-color: #0055b3;
    }
    
    .btn-primary:disabled {
      background-color: #99c2ff;
      cursor: not-allowed;
    }
    
    .social-login {
      margin-top: 2rem;
      text-align: center;
    }
    
    .social-login p {
      color: #666;
      margin-bottom: 1rem;
      position: relative;
    }
    
    .social-login p::before,
    .social-login p::after {
      content: "";
      position: absolute;
      top: 50%;
      width: 35%;
      height: 1px;
      background-color: #ddd;
    }
    
    .social-login p::before {
      left: 0;
    }
    
    .social-login p::after {
      right: 0;
    }
    
    .social-buttons {
      display: flex;
      gap: 1rem;
    }
    
    .btn-google {
      background-color: #db4437;
      color: white;
      flex: 1;
    }
    
    .btn-microsoft {
      background-color: #2f2f2f;
      color: white;
      flex: 1;
    }
    
    .btn-google:hover {
      background-color: #c33d32;
    }
    
    .btn-microsoft:hover {
      background-color: #1f1f1f;
    }
    
    .login-link {
      text-align: center;
      margin-top: 1.5rem;
      color: #666;
    }
    
    .login-link a {
      color: #0066cc;
      text-decoration: none;
      font-weight: 500;
    }
    
    .login-link a:hover {
      text-decoration: underline;
    }
  `
})
export class RegisterComponent {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private oauthService = inject(OAuthService);
  private router = inject(Router);
  
  // Form state
  registerForm: FormGroup;
  
  // Component state
  isLoading = signal(false);
  errorMsg = signal('');
  
  constructor() {
    this.registerForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      confirmPassword: ['', Validators.required]
    }, { validators: this.passwordMatchValidator });
  }
  
  // Form controls getters
  get email() { return this.registerForm.get('email'); }
  get password() { return this.registerForm.get('password'); }
  get confirmPassword() { return this.registerForm.get('confirmPassword'); }
  
  passwordMatchValidator(form: FormGroup) {
    const password = form.get('password')?.value;
    const confirmPassword = form.get('confirmPassword')?.value;
    
    return password === confirmPassword ? null : { passwordMismatch: true };
  }
  
  onSubmit(): void {
    if (this.registerForm.invalid) return;
    
    this.isLoading.set(true);
    this.errorMsg.set('');
    
    const { email, password } = this.registerForm.value;
    
    this.authService.register(email, password).subscribe({
      next: success => {
        this.isLoading.set(false);
        if (success) {
          this.router.navigate(['/dashboard']);
        } else {
          this.errorMsg.set('Registration failed. Please try again.');
        }
      },
      error: error => {
        this.isLoading.set(false);
        if (error.status === 409) {
          this.errorMsg.set('Email already exists. Please try a different email or sign in.');
        } else {
          this.errorMsg.set(error.error?.message || 'An error occurred during registration');
        }
      }
    });
  }
  
  signUpWithGoogle(): void {
    this.oauthService.initiateGoogleLogin();
  }
  
  signUpWithMicrosoft(): void {
    this.oauthService.initiateMicrosoftLogin();
  }
}
