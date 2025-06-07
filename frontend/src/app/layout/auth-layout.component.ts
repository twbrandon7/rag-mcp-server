import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-auth-layout',
  standalone: true,
  imports: [RouterOutlet],
  template: `
    <div class="auth-layout">
      <div class="auth-container">
        <div class="auth-logo">
          <h1>RAG MCP Server</h1>
        </div>
        <div class="auth-content">
          <router-outlet></router-outlet>
        </div>
      </div>
    </div>
  `,
  styles: `
    .auth-layout {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      background-color: #f5f5f5;
    }
    
    .auth-container {
      width: 100%;
      max-width: 400px;
      padding: 2rem;
      background: white;
      border-radius: 8px;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .auth-logo {
      text-align: center;
      margin-bottom: 2rem;
    }
    
    .auth-logo h1 {
      font-size: 1.5rem;
      color: #333;
      font-weight: 600;
    }
    
    .auth-content {
      width: 100%;
    }
  `
})
export class AuthLayoutComponent {
}
