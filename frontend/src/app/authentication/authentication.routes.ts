import { Routes } from '@angular/router';
import { LoginComponent } from './login.component';
import { RegisterComponent } from './register.component';
import { OAuthCallbackComponent } from './oauth-callback.component';
import { noAuthGuard } from '../core/auth.guard';
import { AuthLayoutComponent } from '../layout/auth-layout.component';

export const authRoutes: Routes = [
  {
    path: '',
    component: AuthLayoutComponent,
    canActivate: [noAuthGuard],
    children: [
      { path: 'login', component: LoginComponent },
      { path: 'register', component: RegisterComponent },
      { path: 'callback/:provider', component: OAuthCallbackComponent },
      { path: '', redirectTo: 'login', pathMatch: 'full' }
    ]
  }
];
