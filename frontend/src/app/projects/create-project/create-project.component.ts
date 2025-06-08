import { Component, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ProjectService } from '../project.service';
import { toSignal, toObservable } from '@angular/core/rxjs-interop';
import { switchMap, tap, catchError, of, filter } from 'rxjs';

@Component({
  selector: 'app-create-project',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './create-project.component.html',
  styleUrl: './create-project.component.scss'
})
export class CreateProjectComponent {
  private readonly projectService = inject(ProjectService);
  private readonly router = inject(Router);

  readonly projectName = signal('');
  readonly isLoading = signal(false);
  readonly error = signal<string | null>(null);

  // Signal to trigger project creation
  private readonly createProjectTrigger = signal<number | null>(null);

  // Computed signal for the latest project name to create
  private readonly projectNameToCreate = computed(() => this.projectName().trim());

  // Signal for the result of project creation
  readonly createProjectResult$ = toObservable(this.createProjectTrigger).pipe(
    // Only proceed if the trigger is not null (i.e., user has attempted creation)
    filter((v) => v !== null),
    switchMap(() => {
      const name = this.projectNameToCreate();
      if (!name) {
        this.error.set('Project name is required');
        return of(null);
      }
      this.isLoading.set(true);
      this.error.set(null);
      return this.projectService.createProject$({ project_name: name }).pipe(
        tap({
          next: (project) => {
            this.isLoading.set(false);
            // Navigate to the project detail page
            this.router.navigate(['/dashboard/projects', project.project_id]);
          },
          error: (err) => {
            this.isLoading.set(false);
            this.error.set('Failed to create project. Please try again.');
            console.error('Error creating project:', err);
          }
        }),
        catchError((err) => {
          this.isLoading.set(false);
          this.error.set('Failed to create project. Please try again.');
          return of(null);
        })
      );
    })
  );
  readonly createProjectResult = toSignal(
    this.createProjectResult$,
    { initialValue: null }
  );

  protected createProject(): void {
    // Increment the trigger to start the creation process
    this.createProjectTrigger.set((this.createProjectTrigger() ?? 0) + 1);
  }

  protected cancel(): void {
    this.router.navigate(['/dashboard/projects']);
  }
}
