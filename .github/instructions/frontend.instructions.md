---
applyTo: 'frontend/**'
---
## Project Structure

This project strictly follows the [Angular Style Guide](https://angular.dev/style-guide) to ensure consistency, readability, and maintainability. The structure emphasizes organizing by feature areas rather than file types, with all application code residing in the `src` directory and the main application bootstrap in `main.ts`.

```
frontend/
├── public/                          # Static files
├── src/
│   ├── app/
│   │   ├── core/                   # Singleton services, guards, interceptors
│   │   │   ├── auth.guard.ts
│   │   │   ├── auth.interceptor.ts
│   │   │   ├── auth.service.ts
│   │   │   ├── api.service.ts
│   │   │   └── core.module.ts
│   │   ├── shared/                 # Reusable components, pipes, directives
│   │   │   ├── loading-spinner.component.ts
│   │   │   ├── loading-spinner.component.html
│   │   │   ├── status-badge.component.ts
│   │   │   ├── error-message.component.ts
│   │   │   ├── status-display.pipe.ts
│   │   │   └── shared.module.ts
│   │   ├── authentication/         # User login and registration
│   │   │   ├── login.component.ts
│   │   │   ├── login.component.html
│   │   │   ├── register.component.ts
│   │   │   ├── oauth-callback.component.ts
│   │   │   ├── oauth.service.ts
│   │   │   ├── authentication-routing.module.ts
│   │   │   └── authentication.module.ts
│   │   ├── projects/               # Project management
│   │   │   ├── project-list.component.ts
│   │   │   ├── project-detail.component.ts
│   │   │   ├── create-project.component.ts
│   │   │   ├── project-card.component.ts
│   │   │   ├── project.service.ts
│   │   │   ├── project.model.ts
│   │   │   ├── projects-routing.module.ts
│   │   │   └── projects.module.ts
│   │   ├── url-processing/         # URL submission and status tracking
│   │   │   ├── single-url-form.component.ts
│   │   │   ├── bulk-url-form.component.ts
│   │   │   ├── url-list.component.ts
│   │   │   ├── processing-dashboard.component.ts
│   │   │   ├── url-processing.service.ts
│   │   │   ├── websocket.service.ts
│   │   │   ├── url-submission.model.ts
│   │   │   ├── url-processing-routing.module.ts
│   │   │   └── url-processing.module.ts
│   │   ├── content/                # Data viewing and search
│   │   │   ├── content-viewer.component.ts
│   │   │   ├── vector-search.component.ts
│   │   │   ├── project-sharing.component.ts
│   │   │   ├── content.service.ts
│   │   │   ├── search.service.ts
│   │   │   ├── content.model.ts
│   │   │   ├── content-routing.module.ts
│   │   │   └── content.module.ts
│   │   ├── dashboard/              # Main navigation and overview
│   │   │   ├── main-dashboard.component.ts
│   │   │   ├── sidebar.component.ts
│   │   │   ├── header.component.ts
│   │   │   ├── user-profile.component.ts
│   │   │   ├── dashboard-routing.module.ts
│   │   │   └── dashboard.module.ts
│   │   ├── layout/                 # Application layouts
│   │   │   ├── main-layout.component.ts
│   │   │   ├── main-layout.component.html
│   │   │   ├── auth-layout.component.ts
│   │   │   └── auth-layout.component.html
│   │   ├── app-routing.module.ts
│   │   ├── app.component.ts
│   │   ├── app.component.html
│   │   └── app.module.ts
│   ├── assets/                     # Static assets
│   │   ├── images/
│   │   └── styles/
│   │       ├── _variables.scss
│   │       └── main.scss
│   ├── environments/
│   │   ├── environment.ts
│   │   └── environment.prod.ts
│   ├── main.ts
│   ├── index.html
│   └── styles.css
├── angular.json
├── package.json
├── tsconfig.json
└── README.md
```

## Naming Conventions

Strictly following the [Angular Style Guide naming conventions](https://angular.dev/style-guide#naming):

### File Naming
- **Separate words with hyphens**: Use kebab-case for all file names
  - Example: `user-profile.component.ts`, `auth-guard.service.ts`
- **Match file names to TypeScript identifiers**: File name should reflect the primary class name
  - `UserProfileComponent` → `user-profile.component.ts`
  - `AuthService` → `auth.service.ts`
- **Same name for component files**: TypeScript, template, and styles share the same base name
  - `user-profile.component.ts`
  - `user-profile.component.html` 
  - `user-profile.component.css`
- **Test files with `.spec` suffix**: Unit tests end with `.spec.ts`
  - `user-profile.component.spec.ts`

### Component and Service Naming
- **PascalCase for class names**: `UserProfileComponent`, `AuthService`
- **Descriptive selectors with app prefix**: Use camelCase with consistent prefix
  - Component selector: `app-user-profile`
  - Directive selector: `[appTooltip]` (camelCase for attributes)

### Module Naming
- **Feature modules**: `[feature-name].module.ts`
- **Routing modules**: `[feature-name]-routing.module.ts`
- **Avoid generic names**: No `helpers.ts`, `utils.ts`, or `common.ts`

## Project Organization Principles

Based on the [Angular Style Guide project structure recommendations](https://angular.dev/style-guide#project-structure):

### Core Angular Principles
- **All application code in `src`**: UI code (TypeScript, HTML, styles) lives in the `src` directory
- **Bootstrap in `main.ts`**: Application entry point directly inside `src`
- **One concept per file**: Focus each file on a single concept (one component, service, or directive per file)
- **Organize by feature areas**: Structure by business features, not file types
- **Avoid excessive nesting**: Keep directory structure manageable and navigable

### Directory Organization
- **Feature-based structure**: Each business feature has its own directory
- **Flat when possible**: Avoid unnecessary subdirectories that make navigation difficult
- **Group related files**: Keep components with their templates and styles together
- **Manageable directory sizes**: Split into sub-directories only when a folder becomes hard to navigate

### Core vs Shared vs Features
- **Core**: Singleton services, guards, interceptors (imported once in AppModule)
  - Authentication services, HTTP interceptors, route guards
- **Shared**: Reusable components, pipes, directives (imported in multiple feature modules)
  - UI components, utility pipes, common directives
- **Features**: Self-contained business domains organized by functional area
  - `authentication/`: User login, registration, OAuth
  - `projects/`: Project CRUD operations
  - `url-processing/`: URL submission and processing status
  - `content/`: Data viewing, search, and sharing
  - `dashboard/`: Navigation and overview screens

### Testing Strategy
- **Co-located tests**: Unit tests live alongside the code they test
- **Same directory structure**: Maintain consistency between source and test organization
- **Avoid separate test directories**: No isolated `tests/` folders

### Lazy Loading Architecture
- Feature modules designed for lazy loading to optimize initial bundle size
- Each feature has dedicated routing module for granular route control
- Core module loaded once, shared modules imported where needed

## Angular Coding Standards

Following the [Angular Style Guide coding conventions](https://angular.dev/style-guide):

### Dependency Injection
- **Prefer `inject()` function**: Use `inject()` over constructor parameter injection for better readability and type inference
- **Group Angular properties first**: Inputs, outputs, queries, and lifecycle hooks before methods

### Component Standards
- **Protected for template-only members**: Use `protected` for class members only accessed by templates
- **Readonly for Angular-initialized properties**: Mark `input()`, `output()`, and query properties as `readonly`
- **Meaningful event handler names**: Name handlers for what they do, not the triggering event
  - Prefer: `saveUserData()` over `handleClick()`
- **Simple lifecycle methods**: Keep lifecycle hooks simple, delegate complex logic to well-named methods
- **Implement lifecycle interfaces**: Use TypeScript interfaces (`OnInit`, `OnDestroy`) for type safety

### Template Best Practices
- **Prefer `class` and `style` bindings**: Use direct bindings over `ngClass` and `ngStyle` for better performance
- **Avoid complex template logic**: Move complex logic to TypeScript code, use computed signals for derived values
- **Focus on presentation**: Keep components focused on UI, move business logic to services

### Code Organization
- **Group closely related files**: Keep component files (TS, HTML, CSS, spec) in the same directory when they form a cohesive unit
- **Consistent file organization**: Maintain the same structure across all feature modules
- **Clear separation of concerns**: Components for presentation, services for business logic, modules for organization

This structure supports the application's requirements for user authentication, project management, URL processing, and data visualization while strictly adhering to Angular best practices for scalability and maintainability.
