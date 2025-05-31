# Backend Tests

This directory contains tests for the FastAPI backend application.

## Test Structure

- **`conftest.py`**: Contains test fixtures and setup for database and FastAPI test client
- **`auth/`**: Tests for authentication module
- **`users/`**: Tests for user management module
- **`utils/`**: Tests for utility endpoints

## Running Tests

To run all tests:

```bash
# From backend directory
python -m pytest
```

To run tests with coverage reporting:

```bash
# From backend directory
python -m pytest --cov=src --cov-report=term-missing
```

To generate HTML coverage report:

```bash
# From backend directory
python -m pytest --cov=src --cov-report=html
```

## Test Coverage

Current test coverage: 95%

### Coverage by Module

- Authentication (auth): 93%
- User Management (users): 98%
- Utilities (utils): 100%
- Base application: 94%

## Testing Strategy

1. **Unit Tests**: Test individual functions and methods in isolation
2. **Integration Tests**: Test interactions between components
3. **API Tests**: Test HTTP endpoints using FastAPI's TestClient

## Database Testing

Tests use SQLite in-memory database to provide isolation and speed during testing.
Database fixtures in `conftest.py` handle setup and teardown between tests.

## Mocking Strategy

- External services are mocked to avoid dependencies
- Password hashing is mocked to improve test performance
- Authentication is mocked to avoid dealing with JWT tokens in tests

## CI/CD Integration

Tests are automatically run as part of the CI/CD pipeline to ensure code quality before deployment.
