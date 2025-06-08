import { Component, OnInit, inject, signal, computed, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { toSignal } from '@angular/core/rxjs-interop';
import { switchMap, tap, catchError, of, Subject } from 'rxjs';
import { ProjectService } from '../project.service';
import { ProjectModel } from '../project.model';

@Component({
  selector: 'app-project-detail',
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './project-detail.component.html',
  styleUrl: './project-detail.component.scss'
})
export class ProjectDetailComponent implements OnInit {
  private projectService = inject(ProjectService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);

  readonly projectId = computed(() => this.route.snapshot.paramMap.get('id') || '');

  // Loading and error signals
  readonly isLoading = signal(false);
  readonly error = signal<string | null>(null);
  readonly isEditing = signal(false);
  readonly editProjectName = signal('');

  // Subject to trigger project load
  private readonly loadProjectSubject = new Subject<string>();

  // Project signal (reactively loads project when projectId changes)
  readonly project = toSignal(
    this.loadProjectSubject.pipe(
      switchMap((id: string) => {
        this.isLoading.set(true);
        this.error.set(null);
        return this.projectService.getProject$(id).pipe(
          tap({
            next: () => this.isLoading.set(false),
            error: (err) => {
              this.error.set('Failed to load project. Please try again.');
              this.isLoading.set(false);
              console.error('Error loading project:', err);
            }
          }),
          catchError(() => of(null))
        );
      })
    ),
    { initialValue: null }
  );

  ngOnInit(): void {
    const id = this.projectId();
    if (id) {
      this.loadProjectSubject.next(id);
    }
  }

  protected startEdit(): void {
    const currentProject = this.project() as ProjectModel | null;
    if (currentProject) {
      this.editProjectName.set(currentProject.project_name);
      this.isEditing.set(true);
    }
  }

  protected cancelEdit(): void {
    this.isEditing.set(false);
    this.editProjectName.set('');
  }

  protected saveProject(): void {
    const projectId = this.projectId();
    const newName = this.editProjectName().trim();
    if (!newName || !projectId) {
      return;
    }
    this.isLoading.set(true);
    this.error.set(null);
    this.projectService.updateProject$(projectId, { project_name: newName }).pipe(
      tap({
        next: () => {
          this.isLoading.set(false);
          this.isEditing.set(false);
          this.editProjectName.set('');
        },
        error: (err) => {
          this.error.set('Failed to update project. Please try again.');
          this.isLoading.set(false);
          console.error('Error updating project:', err);
        }
      })
    ).subscribe();
  }

  protected deleteProject(): void {
    const currentProject = this.project() as ProjectModel | null;
    if (!currentProject) {
      return;
    }
    const confirmMessage = `Are you sure you want to delete "${currentProject.project_name}"? This action cannot be undone and will remove all associated data.`;
    if (!confirm(confirmMessage)) {
      return;
    }
    this.isLoading.set(true);
    this.error.set(null);
    this.projectService.deleteProject$(currentProject.project_id).pipe(
      tap({
        next: () => {
          this.isLoading.set(false);
          this.router.navigate(['/dashboard/projects']);
        },
        error: (err) => {
          this.error.set('Failed to delete project. Please try again.');
          this.isLoading.set(false);
          console.error('Error deleting project:', err);
        }
      })
    ).subscribe();
  }

  protected goBack(): void {
    this.router.navigate(['/dashboard/projects']);
  }
}
