import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { AuthService } from '../core/auth.service';

@Component({
  selector: 'app-main-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <div class="dashboard-container">
      <h1>Welcome to the Web Content Vectorization Service</h1>
      
      <div class="welcome-message" *ngIf="authService.user()">
        <p>Hello, {{ authService.user()?.email }}!</p>
      </div>
      
      <div class="dashboard-cards">
        <div class="dashboard-card">
          <h3>Projects</h3>
          <p>Organize your content in projects</p>
          <a routerLink="/projects" class="card-action">Manage Projects</a>
        </div>
        
        <div class="dashboard-card">
          <h3>URL Processing</h3>
          <p>Submit URLs for crawling and vectorization</p>
          <a routerLink="/url-processing" class="card-action">Process URLs</a>
        </div>
        
        <div class="dashboard-card">
          <h3>Content Search</h3>
          <p>Search through your vectorized content</p>
          <a routerLink="/content" class="card-action">Explore Content</a>
        </div>
      </div>
    </div>
  `,
  styles: `
    .dashboard-container {
      padding: 2rem;
    }
    
    h1 {
      margin-bottom: 1.5rem;
      color: #333;
    }
    
    .welcome-message {
      margin-bottom: 2rem;
      padding: 1rem;
      background-color: #f0f7ff;
      border-radius: 8px;
      border-left: 4px solid #0066cc;
    }
    
    .dashboard-cards {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 1.5rem;
    }
    
    .dashboard-card {
      padding: 1.5rem;
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .dashboard-card:hover {
      transform: translateY(-5px);
      box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }
    
    .dashboard-card h3 {
      margin-top: 0;
      color: #0066cc;
    }
    
    .card-action {
      display: inline-block;
      margin-top: 1rem;
      padding: 0.5rem 1rem;
      background-color: #0066cc;
      color: white;
      text-decoration: none;
      border-radius: 4px;
      transition: background-color 0.2s;
    }
    
    .card-action:hover {
      background-color: #0055b3;
    }
  `
})
export class MainDashboardComponent {
  protected authService = inject(AuthService);
}
