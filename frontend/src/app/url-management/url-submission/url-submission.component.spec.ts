import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UrlSubmissionComponent } from './url-submission.component';

describe('UrlSubmissionComponent', () => {
  let component: UrlSubmissionComponent;
  let fixture: ComponentFixture<UrlSubmissionComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UrlSubmissionComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UrlSubmissionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
