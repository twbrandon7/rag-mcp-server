import { Routes } from '@angular/router';
import { ProjectListComponent } from './project-list/project-list.component';
import { ProjectDetailComponent } from './project-detail/project-detail.component';
import { CreateProjectComponent } from './create-project/create-project.component';

export const projectRoutes: Routes = [
  {
    path: '',
    component: ProjectListComponent
  },
  {
    path: 'create',
    component: CreateProjectComponent
  },
  {
    path: ':id',
    component: ProjectDetailComponent
  },
  {
    path: ':id/urls',
    loadChildren: () => import('../url-management/url-management.routes').then(m => m.URL_MANAGEMENT_ROUTES)
  }
];
