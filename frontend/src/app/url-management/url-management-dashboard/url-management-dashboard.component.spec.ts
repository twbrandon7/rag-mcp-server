import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UrlManagementDashboardComponent } from './url-management-dashboard.component';

describe('UrlManagementDashboardComponent', () => {
  let component: UrlManagementDashboardComponent;
  let fixture: ComponentFixture<UrlManagementDashboardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UrlManagementDashboardComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UrlManagementDashboardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
