import { Component, inject, signal, OnInit, OnDestroy } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';
import { Subject, switchMap, Subscription } from 'rxjs';

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
export class LoginComponent implements OnInit, OnDestroy {
  private formBuilder = inject(FormBuilder);
  private authService = inject(AuthService);
  private oauthService = inject(OAuthService);
  private router = inject(Router);
  
  // Subject for login actions
  private loginSubject = new Subject<{email: string, password: string}>();
  private loginSubscription!: Subscription;

  // Form state
  readonly loginForm: FormGroup = this.formBuilder.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(6)]]
  });

  // Component state
  readonly isLoading = signal(false);
  readonly errorMsg = signal('');

  // Form controls getters
  get email() { return this.loginForm.get('email'); }
  get password() { return this.loginForm.get('password'); }

  ngOnInit(): void {
    // Set up the login pipeline
    this.loginSubscription = this.loginSubject.pipe(
      switchMap(({ email, password }) => {
        this.isLoading.set(true);
        this.errorMsg.set('');
        return this.authService.login(email, password);
      })
    ).subscribe({
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

  ngOnDestroy(): void {
    // Complete the subject to clean up subscriptions
    this.loginSubscription.unsubscribe();
  }

  onSubmit(): void {
    if (this.loginForm.invalid) return;

    const { email, password } = this.loginForm.value;
    // Trigger the login subject with the form values
    this.loginSubject.next({ email, password });
  }

  loginWithGoogle(): void {
    this.oauthService.initiateGoogleLogin();
  }

  loginWithMicrosoft(): void {
    this.oauthService.initiateMicrosoftLogin();
  }
}
