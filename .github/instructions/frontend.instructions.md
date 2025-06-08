---
applyTo: 'frontend/**/*.ts,frontend/**/*.html,frontend/**/*.scss'
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
│   │   ├── authentication/         # User login and registration
│   │   ├── projects/
│   │   │   ├── create-project/
│   │   │   │   ├── create-project.component.html
│   │   │   │   ├── create-project.component.scss
│   │   │   │   ├── create-project.component.spec.ts
│   │   │   │   └── create-project.component.ts
│   │   │   ├── project-card/
│   │   │   ├── project-detail/
│   │   │   ├── project-list/
│   │   │   ├── project.model.ts
│   │   │   ├── project.service.spec.ts
│   │   │   ├── project.service.ts
│   │   │   └── projects.routes.ts
│   │   ├── url-processing/         # URL submission and status tracking
│   │   ├── content/                # Data viewing and search
│   │   ├── dashboard/              # Main navigation and overview
│   │   ├── layout/                 # Application layouts
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

## Project Organization Principles

Based on the [Angular Style Guide project structure recommendations](https://angular.dev/style-guide#project-structure):

### Core Angular Principles
- **All application code in `src`**: UI code (TypeScript, HTML, styles) lives in the `src` directory
- **Bootstrap in `main.ts`**: Application entry point directly inside `src`
- **One concept per file**: Focus each file on a single concept (one component, service, or directive per file)
- **Organize by feature areas**: Structure by business features, not file types
- **Avoid excessive nesting**: Keep directory structure manageable and navigable
- **Module is deprecated**: Do not use modules any more; instead, use standalone components and root services where possible.

### Directory Organization
- **Feature-based structure**: Each business feature has its own directory
- **Flat when possible**: Avoid unnecessary subdirectories that make navigation difficult
- **Group related files**: Keep components with their templates and styles together
- **Manageable directory sizes**: Split into sub-directories only when a folder becomes hard to navigate

### Always use Angular CLI to generate code
- Use Angular CLI commands to generate components, services, and other artifacts to ensure consistent structure and naming.
  ```bash
  ng generate component projects/create-project --standalone
  ng generate service authentication/auth
  ```
- Note: never generate modules, as they are deprecated in the latest Angular versions.

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

This structure supports the application's requirements for user authentication, project management, URL processing, and data visualization while strictly adhering to Angular best practices for scalability and maintainability.
