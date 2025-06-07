import { Component, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { AuthService } from '../core/auth.service';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';

@Component({
  selector: 'app-main-layout',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink],
  template: `
    <div class="main-layout">
      <header class="main-header">
        <div class="logo">RAG MCP Server</div>
        <nav class="main-nav">
          <a routerLink="/dashboard" routerLinkActive="active">Dashboard</a>
          <a routerLink="/projects" routerLinkActive="active">Projects</a>
        </nav>
        <div class="user-actions">
          <span class="user-email" *ngIf="authService.user()">{{ authService.user()?.email }}</span>
          <button class="logout-btn" (click)="logout()">Logout</button>
        </div>
      </header>
      
      <main class="main-content">
        <router-outlet></router-outlet>
      </main>
      
      <footer class="main-footer">
        <p>© 2025 RAG MCP Server</p>
      </footer>
    </div>
  `,
  styles: `
    .main-layout {
      display: flex;
      flex-direction: column;
      min-height: 100vh;
    }
    
    .main-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 1rem 2rem;
      background-color: #ffffff;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .logo {
      font-size: 1.5rem;
      font-weight: bold;
      color: #333;
    }
    
    .main-nav {
      display: flex;
      gap: 1.5rem;
    }
    
    .main-nav a {
      color: #555;
      text-decoration: none;
      padding: 0.5rem 0;
      transition: color 0.2s;
    }
    
    .main-nav a:hover {
      color: #0066cc;
    }
    
    .main-nav a.active {
      color: #0066cc;
      font-weight: 500;
      border-bottom: 2px solid #0066cc;
    }
    
    .user-actions {
      display: flex;
      align-items: center;
      gap: 1rem;
    }
    
    .user-email {
      font-size: 0.9rem;
      color: #666;
    }
    
    .logout-btn {
      padding: 0.5rem 1rem;
      background-color: transparent;
      border: 1px solid #ddd;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.2s;
    }
    
    .logout-btn:hover {
      background-color: #f5f5f5;
    }
    
    .main-content {
      flex: 1;
      padding: 2rem;
    }
    
    .main-footer {
      padding: 1rem 2rem;
      background-color: #f5f5f5;
      color: #666;
      text-align: center;
      font-size: 0.9rem;
    }
  `
})
export class MainLayoutComponent {
  protected authService = inject(AuthService);
  private router = inject(Router);
  
  logout() {
    this.authService.logout();
    this.router.navigate(['/auth/login']);
  }
}
