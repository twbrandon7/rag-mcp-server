---
applyTo: 'frontend/**/*.component.ts,frontend/**/*.service.ts'
---
## Services
- If a method in a service returns an `Observable`, the naming of the method should end with `$` to indicate that it returns an observable stream.
  ```typescript
  createProject$(projectData: ProjectCreate): Observable<ProjectResponse> {
    return this.apiService.post<ProjectResponse>('projects', projectData).pipe(
      // ... additional operators
    );
  }
  ```

- In a service, the observable variables should be defined as `private readonly` if applicable, and the observable should be exposed as a signal.
  ```typescript
  private readonly projects$ = this.apiService.get<ProjectResponse[]>('projects').pipe(
    // ... additional operators
  );
  readonly projects = toSignal(this.projects$);
  ```

- If the result of an API response will be shared across the entire application, it should be defined as the declarative form in a root service.
  ```typescript
  type ResourceState<T> =
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: any }
  | { status: 'idle' };

  @Injectable({
    providedIn: 'root'
  })
  export class AuthService {
    // Expose user credential as a signal to allow components to set and access its value reactively
    readonly userCredential = signal<UserCredential | null>(null);
    // Convert to observable for RxJS operators
    private readonly userCredential$ = this.userCredential.asObservable();
    // Fetch user data based on the user credential
    private readonly userData$ = this.userCredential$.pipe(
        switchMap((credential) => {
            if (!credential) {
                return of<ResourceState<UserData>>({ status: 'idle' });
            }

            return this.apiService.get<UserData>(`users/${credential.userId}`).pipe(
                map((data) => ({ status: 'success', data }) as const),
                startWith({ status: 'loading' } as const),
                catchError((error) => of({ status: 'error', error } as const))
            );
        })
    );
    readonly userDataState = toSignal(this.userData$, {
        initialValue: { status: 'idle' } as ResourceState<UserData>
    });
    // Expose user data as a signal
    readonly userData = computed(() =>
        this.userDataState().status === 'success' ? this.userDataState().data : null
    );
    // Expose a variable to indicate if the user data is loading
    readonly isUserDataLoading = computed(() => this.userDataState().status === 'loading');
  }
  ```

## Components
- Prefer `input()` and `output()` over the traditional `@Input()` and `@Output()` decorators.
  ```typescript
  @Component({
    selector: 'app-project',
    templateUrl: './project.component.html',
    styleUrls: ['./project.component.css']
  })
  export class ProjectComponent {
    // Avoid using @Input and @Output
    @input() projectId!: string;
    @output() projectUpdated = new EventEmitter<ProjectResponse>();

    // Prefer using input() and output()
    @input() projectId!: string;
    @output() projectUpdated = new EventEmitter<ProjectResponse>();
  }
  ```

- Avoid using subscribe in components if possible. Instead, convert observables to signals using `toSignal`. Angular will handle the lifecycle of the signal automatically.
  ```typescript
  // Avoid this
  this.authService.userData$.subscribe((data) => {
    this.userData = data;
  });

  // Prefer this
  this.userData = toSignal(this.authService.userData$);
  ```

- Avoid calling a service method that returns an observable directly in a method (except for ngOnInit). Instead, create a signal or subject to receive events and use switchMap to handle the observable.
  ```typescript
  // Avoid this
  handleButtonClick() {
    this.projectService.getProjectData$().subscribe((data) => {
      this.projectData = data;
    });
  }

  // Prefer this
  readonly projectMetadata = signal<ProjectMetadata | null>(null);
  readonly projectData = toObservable(this.projectMetadata).pipe(
    switchMap((metadata) => {
      if (!metadata) {
        return of(null);
      }
      return this.authService.getProject$(metadata);
    })
  );
  handleButtonClick() {
    // Update the projectMetadata signal to trigger the projectData observable
    this.projectMetadata.set({ projectId: '123', name: 'New Project' });
  }
  ```
