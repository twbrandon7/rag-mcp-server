import { Component, OnInit, inject, computed, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { ProjectService } from '../project.service';
import { ProjectModel } from '../project.model';
import { ProjectCardComponent } from '../project-card/project-card.component';

@Component({
  selector: 'app-project-list',
  imports: [CommonModule, RouterModule, ProjectCardComponent],
  templateUrl: './project-list.component.html',
  styleUrl: './project-list.component.scss'
})
export class ProjectListComponent {
  private projectService = inject(ProjectService);
  
  readonly projects = this.projectService.projects;
  readonly isLoading = signal(false);
  readonly error = signal<string | null>(null);
  
  readonly hasProjects = computed(() => this.projects().length > 0);

  protected selectProject(project: ProjectModel): void {
    this.projectService.setSelectedProject(project);
  }

  protected deleteProject(projectId: string): void {
    if (!confirm('Are you sure you want to delete this project? This action cannot be undone.')) {
      return;
    }

    this.isLoading.set(true);
    this.error.set(null);

    this.projectService.deleteProject$(projectId).subscribe({
      next: () => {
        this.isLoading.set(false);
      },
      error: (err) => {
        this.error.set('Failed to delete project. Please try again.');
        this.isLoading.set(false);
        console.error('Error deleting project:', err);
      }
    });
  }
}
