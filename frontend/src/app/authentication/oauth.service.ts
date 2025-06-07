import { Injectable, inject } from '@angular/core';
import { AuthService } from '../core/auth.service';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, from, map, of, switchMap, tap } from 'rxjs';
import { environment } from '../../environments/environment';

// Configuration for OAuth providers
interface OAuthConfig {
  clientId: string;
  redirectUri: string;
  scope: string;
  authorizationEndpoint: string;
}

@Injectable({
  providedIn: 'root'
})
export class OAuthService {
  private authService = inject(AuthService);
  private router = inject(Router);
  private http = inject(HttpClient);
  
  // These would typically come from environment variables in a real app
  private googleConfig: OAuthConfig = {
    clientId: '${GOOGLE_CLIENT_ID}',
    redirectUri: `${window.location.origin}/auth/oauth-callback`,
    scope: 'email profile',
    authorizationEndpoint: 'https://accounts.google.com/o/oauth2/v2/auth'
  };
  
  private microsoftConfig: OAuthConfig = {
    clientId: '${MICROSOFT_CLIENT_ID}',
    redirectUri: `${window.location.origin}/auth/oauth-callback`,
    scope: 'openid profile email',
    authorizationEndpoint: 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize'
  };

  // Initiate Google OAuth flow
  initiateGoogleLogin(): void {
    const authUrl = new URL(this.googleConfig.authorizationEndpoint);
    authUrl.searchParams.append('client_id', this.googleConfig.clientId);
    authUrl.searchParams.append('redirect_uri', this.googleConfig.redirectUri);
    authUrl.searchParams.append('scope', this.googleConfig.scope);
    authUrl.searchParams.append('response_type', 'token');
    authUrl.searchParams.append('state', 'google');
    
    window.location.href = authUrl.toString();
  }
  
  // Initiate Microsoft OAuth flow
  initiateMicrosoftLogin(): void {
    const authUrl = new URL(this.microsoftConfig.authorizationEndpoint);
    authUrl.searchParams.append('client_id', this.microsoftConfig.clientId);
    authUrl.searchParams.append('redirect_uri', this.microsoftConfig.redirectUri);
    authUrl.searchParams.append('scope', this.microsoftConfig.scope);
    authUrl.searchParams.append('response_type', 'token');
    authUrl.searchParams.append('state', 'microsoft');
    
    window.location.href = authUrl.toString();
  }
  
  // Handle the OAuth callback
  handleCallback(fragment: string): Observable<boolean> {
    const params = new URLSearchParams(fragment);
    const accessToken = params.get('access_token');
    const state = params.get('state');
    const error = params.get('error');
    
    if (error) {
      console.error('OAuth error:', error);
      return of(false);
    }
    
    if (!accessToken) {
      console.error('No access token received');
      return of(false);
    }
    
    if (state === 'google') {
      return this.authService.googleLogin(accessToken);
    } else if (state === 'microsoft') {
      return this.authService.microsoftLogin(accessToken);
    } else {
      console.error('Unknown OAuth provider');
      return of(false);
    }
  }
}
