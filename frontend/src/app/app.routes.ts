import { Routes } from '@angular/router';
import { authRoutes } from './authentication/authentication.routes';
import { dashboardRoutes } from './dashboard/dashboard.routes';
import { projectRoutes } from './projects/projects.routes';

export const routes: Routes = [
  {
    path: 'auth',
    children: authRoutes
  },
  {
    path: 'dashboard',
    children: dashboardRoutes
  },
  {
    path: 'projects',
    children: projectRoutes
  },
  {
    path: '',
    redirectTo: 'dashboard',
    pathMatch: 'full'
  }
];
