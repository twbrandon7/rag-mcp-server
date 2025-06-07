import { HttpClient } from '@angular/common/http';
import { Injectable, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { Observable, catchError, map, of, tap } from 'rxjs';
import { environment } from '../../environments/environment';
import { jwtDecode } from 'jwt-decode';

export interface User {
  id: string;
  email: string;
  name?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);
  
  // Using signals for reactive state
  private _user = signal<User | null>(null);
  private _isAuthenticated = signal<boolean>(false);
  
  // Public readonly signals
  readonly user = this._user.asReadonly();
  readonly isAuthenticated = this._isAuthenticated.asReadonly();

  constructor() {
    this.checkAuthStatus();
  }

  login(email: string, password: string): Observable<boolean> {
    return this.http.post<AuthResponse>(`${environment.authUrl}/login`, { email, password })
      .pipe(
        tap(response => this.handleAuthSuccess(response)),
        map(() => true),
        catchError(error => {
          console.error('Login error:', error);
          return of(false);
        })
      );
  }

  register(email: string, password: string): Observable<boolean> {
    return this.http.post<AuthResponse>(`${environment.authUrl}/register`, { email, password })
      .pipe(
        tap(response => this.handleAuthSuccess(response)),
        map(() => true),
        catchError(error => {
          console.error('Registration error:', error);
          return of(false);
        })
      );
  }

  googleLogin(token: string): Observable<boolean> {
    return this.http.post<AuthResponse>(`${environment.authUrl}/google`, { token })
      .pipe(
        tap(response => this.handleAuthSuccess(response)),
        map(() => true),
        catchError(error => {
          console.error('Google login error:', error);
          return of(false);
        })
      );
  }

  microsoftLogin(token: string): Observable<boolean> {
    return this.http.post<AuthResponse>(`${environment.authUrl}/microsoft`, { token })
      .pipe(
        tap(response => this.handleAuthSuccess(response)),
        map(() => true),
        catchError(error => {
          console.error('Microsoft login error:', error);
          return of(false);
        })
      );
  }

  logout(): void {
    localStorage.removeItem('access_token');
    this._user.set(null);
    this._isAuthenticated.set(false);
    this.router.navigate(['/auth/login']);
  }

  checkAuthStatus(): void {
    const token = this.getToken();
    if (token) {
      try {
        const decoded: any = jwtDecode(token);
        const currentTime = Date.now() / 1000;
        
        if (decoded.exp && decoded.exp > currentTime) {
          // Token is valid
          this._isAuthenticated.set(true);
          this._user.set({
            id: decoded.sub,
            email: decoded.email,
            name: decoded.name
          });
        } else {
          // Token expired
          this.logout();
        }
      } catch (error) {
        // Invalid token
        this.logout();
      }
    }
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  private handleAuthSuccess(response: AuthResponse): void {
    localStorage.setItem('access_token', response.access_token);
    this._user.set(response.user);
    this._isAuthenticated.set(true);
  }
}
