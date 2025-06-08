import { Injectable, inject, signal } from '@angular/core';
import { Observable, scan, startWith, Subject, switchMap, tap } from 'rxjs';
import { ApiService } from '../core/api.service';
import { ProjectModel, ProjectCreate, ProjectUpdate, ProjectResponse } from './project.model';
import { toSignal } from '@angular/core/rxjs-interop';

@Injectable({
  providedIn: 'root'
})
export class ProjectService {
  private apiService = inject(ApiService);

  // Signal for managing project state
  private readonly projectsUpdate = new Subject<void>();
  readonly projectsUpdate$ = this.projectsUpdate.asObservable().pipe(
    // Increase an internal counter to trigger updates
    scan((acc, _) => acc + 1, 0),
    startWith(0),
  );
  private readonly projects$ = this.projectsUpdate$.pipe(
    switchMap(() => this.apiService.get<ProjectModel[]>('projects')),
  );
  readonly projects = toSignal(this.projects$, {
    initialValue: [],
  });

  private readonly _selectedProject = signal<ProjectModel | null>(null);
  readonly selectedProject = this._selectedProject.asReadonly();

  /**
   * Create a new project
   */
  createProject$(projectData: ProjectCreate): Observable<ProjectResponse> {
    return this.apiService.post<ProjectResponse>('projects', projectData).pipe(
      tap(() => this.projectsUpdate.next()),
    );
  }

  
  /**
   * Get a specific project by ID
   */
  getProject$(projectId: string): Observable<ProjectModel> {
    return this.apiService.get<ProjectModel>(`projects/${projectId}`).pipe(
      tap(project => {
        this._selectedProject.set(project);
      })
    );
  }

  /**
   * Update a project
   */
  updateProject$(projectId: string, projectData: ProjectUpdate): Observable<ProjectResponse> {
    return this.apiService.patch<ProjectResponse>(`projects/${projectId}`, projectData).pipe(
      tap(() => this.projectsUpdate.next()),
    );
  }

  /**
   * Delete a project
   */
  deleteProject$(projectId: string): Observable<void> {
    return this.apiService.delete<void>(`projects/${projectId}`).pipe(
      tap(() => this.projectsUpdate.next()),
    );
  }

  /**
   * Set selected project
   */
  setSelectedProject(project: ProjectModel | null): void {
    this._selectedProject.set(project);
  }
}
