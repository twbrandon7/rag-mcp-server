import { Routes } from '@angular/router';
import { MainDashboardComponent } from './dashboard.component';
import { authGuard } from '../core/auth.guard';
import { MainLayoutComponent } from '../layout/main-layout.component';
import { projectRoutes } from '../projects/projects.routes';

export const dashboardRoutes: Routes = [
  {
    path: '',
    component: MainLayoutComponent,
    canActivate: [authGuard],
    children: [
      { path: '', component: MainDashboardComponent },
      { 
        path: 'projects', 
        children: projectRoutes 
      }
    ]
  }
];
