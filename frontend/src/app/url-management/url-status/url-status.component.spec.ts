import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UrlStatusComponent } from './url-status.component';

describe('UrlStatusComponent', () => {
  let component: UrlStatusComponent;
  let fixture: ComponentFixture<UrlStatusComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UrlStatusComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UrlStatusComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
