import { Component, inject, input, output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { ProjectModel } from '../project.model';

@Component({
  selector: 'app-project-card',
  standalone: true,
  imports: [CommonModule, RouterModule, ButtonModule],
  templateUrl: './project-card.component.html',
  styleUrl: './project-card.component.scss'
})
export class ProjectCardComponent {
  readonly project = input<ProjectModel>();
  readonly delete = output<string>();
  readonly select = output<ProjectModel>();
  readonly router = inject(Router);

  protected deleteProject(event: Event): void {
    event.stopPropagation();
    if (this.project()) {
      this.delete.emit(this.project()!.project_id);
    }
  }

  protected selectProject(): void {
    if (this.project()) {
      this.select.emit(this.project()!);
      this.router.navigate(['/dashboard/projects', this.project()!.project_id]);
    }
  }
}
