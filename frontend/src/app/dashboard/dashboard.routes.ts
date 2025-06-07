import { Routes } from '@angular/router';
import { MainDashboardComponent } from './main-dashboard.component';
import { authGuard } from '../core/auth.guard';
import { MainLayoutComponent } from '../layout/main-layout.component';

export const dashboardRoutes: Routes = [
  {
    path: '',
    component: MainLayoutComponent,
    canActivate: [authGuard],
    children: [
      { path: '', component: MainDashboardComponent }
    ]
  }
];
