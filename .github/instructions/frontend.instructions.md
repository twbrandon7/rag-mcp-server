---
applyTo: 'frontend/**'
---
## Project Structure

Following Angular style guide principles, the project is organized by feature areas rather than file types. This structure promotes consistency, readability, and maintainability across the application.

```
frontend/
├── public/                          # Static files
├── src/
│   ├── app/                        # Main application logic
│   │   ├── core/                   # Singleton services, guards, interceptors
│   │   │   ├── auth/              # Authentication guards and interceptors
│   │   │   │   ├── auth.guard.ts
│   │   │   │   ├── auth.interceptor.ts
│   │   │   │   └── auth.guard.spec.ts
│   │   │   ├── services/          # Core application services
│   │   │   │   ├── auth.service.ts
│   │   │   │   ├── api.service.ts
│   │   │   │   └── auth.service.spec.ts
│   │   │   └── core.module.ts     # Core module (import once in AppModule)
│   │   ├── shared/                # Shared components, directives, pipes
│   │   │   ├── components/        # Reusable UI components
│   │   │   │   ├── loading-spinner/
│   │   │   │   │   ├── loading-spinner.component.ts
│   │   │   │   │   ├── loading-spinner.component.html
│   │   │   │   │   ├── loading-spinner.component.css
│   │   │   │   │   └── loading-spinner.component.spec.ts
│   │   │   │   ├── status-badge/
│   │   │   │   │   ├── status-badge.component.ts
│   │   │   │   │   ├── status-badge.component.html
│   │   │   │   │   ├── status-badge.component.css
│   │   │   │   │   └── status-badge.component.spec.ts
│   │   │   │   └── error-message/
│   │   │   │       ├── error-message.component.ts
│   │   │   │       ├── error-message.component.html
│   │   │   │       ├── error-message.component.css
│   │   │   │       └── error-message.component.spec.ts
│   │   │   ├── pipes/             # Custom pipes
│   │   │   │   ├── status-display.pipe.ts
│   │   │   │   └── status-display.pipe.spec.ts
│   │   │   ├── directives/        # Custom directives
│   │   │   └── shared.module.ts   # Shared module
│   │   ├── features/              # Feature modules organized by business domain
│   │   │   ├── authentication/    # User authentication feature
│   │   │   │   ├── components/
│   │   │   │   │   ├── login/
│   │   │   │   │   │   ├── login.component.ts
│   │   │   │   │   │   ├── login.component.html
│   │   │   │   │   │   ├── login.component.css
│   │   │   │   │   │   └── login.component.spec.ts
│   │   │   │   │   ├── register/
│   │   │   │   │   │   ├── register.component.ts
│   │   │   │   │   │   ├── register.component.html
│   │   │   │   │   │   ├── register.component.css
│   │   │   │   │   │   └── register.component.spec.ts
│   │   │   │   │   └── oauth-callback/
│   │   │   │   │       ├── oauth-callback.component.ts
│   │   │   │   │       ├── oauth-callback.component.html
│   │   │   │   │       ├── oauth-callback.component.css
│   │   │   │   │       └── oauth-callback.component.spec.ts
│   │   │   │   ├── services/
│   │   │   │   │   ├── oauth.service.ts
│   │   │   │   │   └── oauth.service.spec.ts
│   │   │   │   ├── authentication-routing.module.ts
│   │   │   │   └── authentication.module.ts
│   │   │   ├── project-management/  # Project CRUD operations
│   │   │   │   ├── components/
│   │   │   │   │   ├── project-list/
│   │   │   │   │   │   ├── project-list.component.ts
│   │   │   │   │   │   ├── project-list.component.html
│   │   │   │   │   │   ├── project-list.component.css
│   │   │   │   │   │   └── project-list.component.spec.ts
│   │   │   │   │   ├── project-detail/
│   │   │   │   │   │   ├── project-detail.component.ts
│   │   │   │   │   │   ├── project-detail.component.html
│   │   │   │   │   │   ├── project-detail.component.css
│   │   │   │   │   │   └── project-detail.component.spec.ts
│   │   │   │   │   ├── create-project/
│   │   │   │   │   │   ├── create-project.component.ts
│   │   │   │   │   │   ├── create-project.component.html
│   │   │   │   │   │   ├── create-project.component.css
│   │   │   │   │   │   └── create-project.component.spec.ts
│   │   │   │   │   └── project-card/
│   │   │   │   │       ├── project-card.component.ts
│   │   │   │   │       ├── project-card.component.html
│   │   │   │   │       ├── project-card.component.css
│   │   │   │   │       └── project-card.component.spec.ts
│   │   │   │   ├── services/
│   │   │   │   │   ├── project.service.ts
│   │   │   │   │   └── project.service.spec.ts
│   │   │   │   ├── models/
│   │   │   │   │   └── project.model.ts
│   │   │   │   ├── project-management-routing.module.ts
│   │   │   │   └── project-management.module.ts
│   │   │   ├── url-processing/     # URL submission and processing
│   │   │   │   ├── components/
│   │   │   │   │   ├── url-submission/
│   │   │   │   │   │   ├── single-url-form/
│   │   │   │   │   │   │   ├── single-url-form.component.ts
│   │   │   │   │   │   │   ├── single-url-form.component.html
│   │   │   │   │   │   │   ├── single-url-form.component.css
│   │   │   │   │   │   │   └── single-url-form.component.spec.ts
│   │   │   │   │   │   ├── bulk-url-form/
│   │   │   │   │   │   │   ├── bulk-url-form.component.ts
│   │   │   │   │   │   │   ├── bulk-url-form.component.html
│   │   │   │   │   │   │   ├── bulk-url-form.component.css
│   │   │   │   │   │   │   └── bulk-url-form.component.spec.ts
│   │   │   │   │   │   └── url-submission.component.ts
│   │   │   │   │   ├── url-status/
│   │   │   │   │   │   ├── url-list/
│   │   │   │   │   │   │   ├── url-list.component.ts
│   │   │   │   │   │   │   ├── url-list.component.html
│   │   │   │   │   │   │   ├── url-list.component.css
│   │   │   │   │   │   │   └── url-list.component.spec.ts
│   │   │   │   │   │   ├── url-item/
│   │   │   │   │   │   │   ├── url-item.component.ts
│   │   │   │   │   │   │   ├── url-item.component.html
│   │   │   │   │   │   │   ├── url-item.component.css
│   │   │   │   │   │   │   └── url-item.component.spec.ts
│   │   │   │   │   │   └── processing-dashboard/
│   │   │   │   │   │       ├── processing-dashboard.component.ts
│   │   │   │   │   │       ├── processing-dashboard.component.html
│   │   │   │   │   │       ├── processing-dashboard.component.css
│   │   │   │   │   │       └── processing-dashboard.component.spec.ts
│   │   │   │   ├── services/
│   │   │   │   │   ├── url-processing.service.ts
│   │   │   │   │   ├── websocket.service.ts
│   │   │   │   │   ├── url-processing.service.spec.ts
│   │   │   │   │   └── websocket.service.spec.ts
│   │   │   │   ├── models/
│   │   │   │   │   ├── url-submission.model.ts
│   │   │   │   │   └── processing-status.model.ts
│   │   │   │   ├── url-processing-routing.module.ts
│   │   │   │   └── url-processing.module.ts
│   │   │   ├── data-management/    # View and manage processed data
│   │   │   │   ├── components/
│   │   │   │   │   ├── content-viewer/
│   │   │   │   │   │   ├── content-viewer.component.ts
│   │   │   │   │   │   ├── content-viewer.component.html
│   │   │   │   │   │   ├── content-viewer.component.css
│   │   │   │   │   │   └── content-viewer.component.spec.ts
│   │   │   │   │   ├── vector-search/
│   │   │   │   │   │   ├── vector-search.component.ts
│   │   │   │   │   │   ├── vector-search.component.html
│   │   │   │   │   │   ├── vector-search.component.css
│   │   │   │   │   │   └── vector-search.component.spec.ts
│   │   │   │   │   └── project-sharing/
│   │   │   │   │       ├── project-sharing.component.ts
│   │   │   │   │       ├── project-sharing.component.html
│   │   │   │   │       ├── project-sharing.component.css
│   │   │   │   │       └── project-sharing.component.spec.ts
│   │   │   │   ├── services/
│   │   │   │   │   ├── content.service.ts
│   │   │   │   │   ├── search.service.ts
│   │   │   │   │   ├── content.service.spec.ts
│   │   │   │   │   └── search.service.spec.ts
│   │   │   │   ├── models/
│   │   │   │   │   ├── content.model.ts
│   │   │   │   │   └── search-result.model.ts
│   │   │   │   ├── data-management-routing.module.ts
│   │   │   │   └── data-management.module.ts
│   │   │   └── dashboard/          # Main dashboard and navigation
│   │   │       ├── components/
│   │   │       │   ├── main-dashboard/
│   │   │       │   │   ├── main-dashboard.component.ts
│   │   │       │   │   ├── main-dashboard.component.html
│   │   │       │   │   ├── main-dashboard.component.css
│   │   │       │   │   └── main-dashboard.component.spec.ts
│   │   │       │   ├── navigation/
│   │   │       │   │   ├── sidebar/
│   │   │       │   │   │   ├── sidebar.component.ts
│   │   │       │   │   │   ├── sidebar.component.html
│   │   │       │   │   │   ├── sidebar.component.css
│   │   │       │   │   │   └── sidebar.component.spec.ts
│   │   │       │   │   └── header/
│   │   │       │   │       ├── header.component.ts
│   │   │       │   │       ├── header.component.html
│   │   │       │   │       ├── header.component.css
│   │   │       │   │       └── header.component.spec.ts
│   │   │       │   └── user-profile/
│   │   │       │       ├── user-profile.component.ts
│   │   │       │       ├── user-profile.component.html
│   │   │       │       ├── user-profile.component.css
│   │   │       │       └── user-profile.component.spec.ts
│   │   │       ├── dashboard-routing.module.ts
│   │   │       └── dashboard.module.ts
│   │   ├── layout/                 # Layout components
│   │   │   ├── main-layout/
│   │   │   │   ├── main-layout.component.ts
│   │   │   │   ├── main-layout.component.html
│   │   │   │   ├── main-layout.component.css
│   │   │   │   └── main-layout.component.spec.ts
│   │   │   └── auth-layout/
│   │   │       ├── auth-layout.component.ts
│   │   │       ├── auth-layout.component.html
│   │   │       ├── auth-layout.component.css
│   │   │       └── auth-layout.component.spec.ts
│   │   ├── app-routing.module.ts   # Main routing configuration
│   │   ├── app.component.ts        # Root component
│   │   ├── app.component.html      # Root template
│   │   ├── app.component.css       # Root styles
│   │   ├── app.component.spec.ts   # Root component tests
│   │   └── app.module.ts           # Root module
│   ├── assets/                     # Static assets
│   │   ├── images/
│   │   ├── icons/
│   │   └── styles/                 # Global styles
│   │       ├── _variables.scss
│   │       ├── _mixins.scss
│   │       └── main.scss
│   ├── environments/               # Environment configurations
│   │   ├── environment.ts          # Development environment
│   │   └── environment.prod.ts     # Production environment
│   ├── main.ts                     # Application bootstrap
│   ├── index.html                  # Main HTML file
│   └── styles.css                  # Global styles
├── angular.json                    # Angular CLI configuration
├── package.json                    # Dependencies and scripts
├── tsconfig.json                   # TypeScript configuration
├── tsconfig.app.json              # App-specific TypeScript config
├── tsconfig.spec.json             # Test-specific TypeScript config
└── README.md                       # Project documentation
```

## Naming Conventions

Following Angular style guide recommendations:

### Files
- Use **kebab-case** for file names: `user-profile.component.ts`
- Match file names to their primary TypeScript identifier
- Use descriptive suffixes: `.component.ts`, `.service.ts`, `.guard.ts`, `.pipe.ts`
- Test files end with `.spec.ts`: `user-profile.component.spec.ts`

### Components
- Use **PascalCase** for class names: `UserProfileComponent`
- Use **camelCase** with application prefix for selectors: `app-user-profile`
- Group related files in the same directory

### Services
- Use **PascalCase** for class names: `AuthService`
- Use **camelCase** for file names: `auth.service.ts`

### Modules
- Feature modules follow the pattern: `[feature-name].module.ts`
- Routing modules: `[feature-name]-routing.module.ts`

## Project Organization Principles

### Feature-Based Structure
- Organize by business features rather than file types
- Each feature module is self-contained with its own components, services, and routing
- Shared functionality goes in the `shared/` directory

### Core vs Shared
- **Core**: Singleton services, guards, interceptors (imported once in AppModule)
- **Shared**: Reusable components, pipes, directives (imported in multiple modules)

### Lazy Loading
- Feature modules are designed for lazy loading to improve initial load time
- Each feature has its own routing module for granular route control

### Testing Strategy
- Unit tests alongside their corresponding files
- Integration tests in feature directories
- End-to-end tests in separate `e2e/` directory (if applicable)

This structure supports the application's requirements for user authentication, project management, URL processing, and data visualization while maintaining Angular best practices for scalability and maintainability.
