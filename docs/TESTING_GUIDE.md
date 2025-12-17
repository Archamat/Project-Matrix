# Testing Guide for Project-Matrix

## Overview

This document explains the comprehensive unit testing setup implemented for the Project-Matrix application, focusing on the projects module. The testing infrastructure uses **pytest** with **Flask test utilities** and an **in-memory SQLite database** for fast, isolated tests.

---

## Table of Contents

1. [Testing Architecture](#testing-architecture)
2. [Setup and Configuration](#setup-and-configuration)
3. [How Tests Work](#how-tests-work)
4. [Test Coverage](#test-coverage)
5. [Running Tests](#running-tests)
6. [CI/CD Integration](#cicd-integration)
7. [Writing New Tests](#writing-new-tests)

---

## Testing Architecture

### Philosophy

Our testing strategy follows these principles:

- **Isolation**: Each test runs in a clean environment with no side effects
- **Speed**: Tests complete in milliseconds using in-memory database
- **Realism**: Real database operations (not mocked) for accurate behavior testing
- **Coverage**: Comprehensive tests for business logic, data layer, and models
- **Maintainability**: Clear test organization and descriptive names

### Test Pyramid

```
        /\
       /  \        E2E Tests (Future)
      /----\       - Full browser automation
     /      \      - User workflow testing
    /--------\
   /  API     \    API Tests (Future)
  /   Tests    \   - HTTP endpoint testing
 /--------------\  - JSON request/response
/                \ 
|  Unit Tests    | Unit Tests (Current - 22 tests)
|  (Current)     | - Business logic
|________________| - Database operations
                   - Model validation
```

---

## Setup and Configuration

### Dependencies

Added to `requirements.txt`:

```txt
pytest==8.0.0          # Testing framework
pytest-flask==1.3.0    # Flask-specific fixtures
pytest-cov==7.0.0      # Coverage reporting
```

### Configuration Files

#### 1. `pytest.ini` - Pytest Configuration

```ini
[pytest]
pythonpath = .              # Add project root to Python path
testpaths = tests           # Where to find tests
python_files = test_*.py    # Test file naming pattern
python_classes = Test*      # Test class naming pattern
python_functions = test_*   # Test function naming pattern
addopts = -v --tb=short     # Verbose output, short tracebacks
```

**Why these settings?**
- `pythonpath = .` allows `from app import ...` to work in tests
- `testpaths = tests` tells pytest where to look for tests
- Naming patterns follow pytest conventions
- `-v` gives detailed output showing each test result
- `--tb=short` keeps error messages concise

#### 2. `tests/conftest.py` - Shared Fixtures

```python
@pytest.fixture(scope='session')
def app():
    """Create application for testing"""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
```

**Key Configuration Choices:**

- **`scope='session'`**: Creates app once per test session (performance optimization)
- **`sqlite:///:memory:`**: Database exists only in RAM, destroyed after tests
- **`TESTING = True`**: Enables Flask testing mode (better error messages)
- **`WTF_CSRF_ENABLED = False`**: Disables CSRF tokens for easier testing
- **`db.create_all()`**: Creates all tables before tests
- **`db.drop_all()`**: Cleans up after all tests complete

---

## How Tests Work

### In-Memory Database: The Magic Behind the Tests

#### What is `sqlite:///:memory:`?

When you see this URI in the test configuration, it creates a **temporary SQLite database entirely in RAM**:

```
Production:  PostgreSQL on disk  → persists forever
Development: SQLite on disk      → data.db file
Testing:     SQLite in memory    → gone after tests
```

#### The Test Lifecycle

```
┌─────────────────────────────────────────────────────────┐
│ Test Session Starts                                     │
├─────────────────────────────────────────────────────────┤
│ 1. pytest loads conftest.py                            │
│ 2. @pytest.fixture(scope='session') creates app        │
│ 3. SQLite database created in RAM                      │
│ 4. db.create_all() creates tables:                     │
│    - users                                              │
│    - projects                                           │
│    - applications                                       │
│    - tasks                                              │
│    - chat_messages                                      │
│    - project_links                                      │
│    - project_notes                                      │
├─────────────────────────────────────────────────────────┤
│ Test 1: test_create_project_success                    │
│ - Creates test user (INSERT into users)                │
│ - Calls handle_project_create()                        │
│ - Commits to database (in RAM)                         │
│ - Queries database to verify                           │
│ - Assertions pass ✓                                    │
├─────────────────────────────────────────────────────────┤
│ Test 2: test_create_project_with_other_skill           │
│ - Previous data still in memory!                       │
│ - Creates another project                              │
│ - Verifies custom skill handling                       │
│ - Assertions pass ✓                                    │
├─────────────────────────────────────────────────────────┤
│ ... (20 more tests) ...                                │
├─────────────────────────────────────────────────────────┤
│ Test Session Ends                                       │
│ - db.drop_all() destroys all tables                    │
│ - Memory freed by Python garbage collector             │
│ - No trace left on disk                                │
└─────────────────────────────────────────────────────────┘
```

#### Real Database Operations

**This is NOT mocking!** Your tests perform actual database operations:

```python
def test_create_project_success(self, app, test_user):
    with app.app_context():
        # This does a REAL SQL INSERT
        handle_project_create(
            name='New Project',
            description='A great project',
            sector='Technology',
            people_count=3,
            skills=['Python', 'JavaScript'],
            creator_id=test_user
        )
        
        # This does a REAL SQL SELECT
        project = Project.query.filter_by(name='New Project').first()
        
        # Verify it worked
        assert project is not None
```

**Behind the scenes:**
```sql
-- handle_project_create() executes:
INSERT INTO projects (name, description, sector, people_count, skills, creator_id)
VALUES ('New Project', 'A great project', 'Technology', 3, 'Python, JavaScript', 1);

-- Project.query.filter_by() executes:
SELECT * FROM projects WHERE name = 'New Project' LIMIT 1;
```

### Test Isolation

Each test fixture provides isolation:

```python
@pytest.fixture
def test_user(app):
    """Create a test user"""
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user.id  # Return ID, user object stays in session
```

**Why return `user.id`?**
- User object is tied to the session in the fixture
- Returning ID lets tests fetch fresh user objects in their own context
- Prevents "DetachedInstanceError" from SQLAlchemy

---

## Test Coverage

### Current Coverage: 22 Tests (100% Pass Rate)

```
Total Coverage: 67% of projects module
- Database Manager: 93%
- Models: 100%
- Business Logic: 41%
- API Endpoints: 34% (not yet tested)
```

### Test Breakdown

#### 1. Project Creation Tests (5 tests)

```python
class TestProjectCreation:
    def test_create_project_success(...)
    def test_create_project_with_other_skill(...)
    def test_create_project_short_name(...)
    def test_create_project_empty_name(...)
    def test_create_project_strips_whitespace(...)
```

**What these tests verify:**
- ✅ Valid projects are created successfully
- ✅ Custom "Other" skills are appended correctly
- ✅ Short names (< 3 chars) are rejected with ValueError
- ✅ Empty/whitespace-only names are rejected
- ✅ Leading/trailing whitespace is stripped from names

**Example validation test:**
```python
def test_create_project_short_name(self, app, test_user):
    with app.app_context():
        with pytest.raises(ValueError, match="at least 3 characters"):
            handle_project_create(
                name='AB',  # Only 2 characters
                description='Test',
                sector='Tech',
                people_count=1,
                creator_id=test_user
            )
```

#### 2. Project Retrieval Tests (4 tests)

```python
class TestProjectRetrieval:
    def test_get_project_by_id(...)
    def test_get_project_by_invalid_id(...)
    def test_get_all_projects(...)
    def test_project_to_dict(...)
```

**What these tests verify:**
- ✅ Projects can be retrieved by valid ID
- ✅ Invalid IDs return None (not crash)
- ✅ get_all_projects() returns all projects
- ✅ to_dict() serialization works correctly

**Example serialization test:**
```python
def test_project_to_dict(self, app, test_project):
    with app.app_context():
        project = Project.query.get(test_project)
        data = project.to_dict()
        
        assert data['id'] == test_project
        assert data['name'] == 'Test Project'
        assert isinstance(data['skills'], list)  # Comma-separated → list
        assert 'Python' in data['skills']
```

#### 3. Application Tests (3 tests)

```python
class TestProjectApplications:
    def test_apply_to_project(...)
    def test_get_project_applicants(...)
    def test_get_applicants_unauthorized(...)
```

**What these tests verify:**
- ✅ Users can apply to projects
- ✅ Project creators can view applicants
- ✅ Non-creators are blocked from viewing applicants

**Example authorization test:**
```python
def test_get_applicants_unauthorized(self, app, test_project, test_user):
    with app.app_context():
        # Create another user (not creator)
        other_user = User(username='other', email='other@test.com')
        other_user.set_password('password')
        db.session.add(other_user)
        db.session.commit()
        
        # Should raise PermissionError
        with pytest.raises(PermissionError, match="don't have permission"):
            get_project_applicants(test_project, other_user.id)
```

#### 4. Database Manager Tests (4 tests)

```python
class TestProjectDatabaseManager:
    def test_create_project_via_manager(...)
    def test_create_project_invalid_creator(...)
    def test_add_element_to_project(...)
    def test_delete_element_from_project(...)
```

**What these tests verify:**
- ✅ ProjectDatabaseManager can create projects
- ✅ Invalid creator IDs raise ValueError
- ✅ Elements (tasks, links) can be added to projects
- ✅ Elements can be deleted from projects

**Example database operation test:**
```python
def test_add_element_to_project(self, app, test_project):
    with app.app_context():
        manager = ProjectDatabaseManager()
        
        # Add a task
        task = Task(project_id=test_project, title='Test Task')
        result = manager.add_element_to_project(test_project, task)
        
        assert result.id is not None
        assert result.title == 'Test Task'
        
        # Verify relationship
        project = Project.query.get(test_project)
        assert len(project.tasks) == 1
```

#### 5. Model Tests (6 tests)

```python
class TestProjectModels:
    def test_task_creation(...)
    def test_task_toggle(...)
    def test_chat_message_creation(...)
    def test_project_link_creation(...)
    def test_project_note_creation(...)
    def test_project_relationships(...)
```

**What these tests verify:**
- ✅ All model types can be created
- ✅ Task completion can be toggled
- ✅ Timestamps are automatically set (created_at)
- ✅ Relationships between models work correctly

**Example relationship test:**
```python
def test_project_relationships(self, app, test_project, test_user):
    with app.app_context():
        project = Project.query.get(test_project)
        
        # Add related entities
        task = Task(project_id=test_project, title='Task 1')
        message = ChatMessage(project_id=test_project, author_id=test_user, body='Message 1')
        link = ProjectLink(project_id=test_project, label='Link 1', url='http://test.com')
        note = ProjectNote(project_id=test_project, author_id=test_user, content='Note 1')
        
        db.session.add_all([task, message, link, note])
        db.session.commit()
        
        # Verify all relationships
        db.session.refresh(project)
        assert len(project.tasks) == 1
        assert len(project.messages) == 1
        assert len(project.links) == 1
        assert len(project.notes) == 1
```

---

## Running Tests

### Local Development

#### Run all tests
```bash
pytest tests/test_project.py -v
```

**Output:**
```
tests/test_project.py::TestProjectCreation::test_create_project_success PASSED [ 4%]
tests/test_project.py::TestProjectCreation::test_create_project_with_other_skill PASSED [ 9%]
...
================================================= 22 passed in 8.94s =================================================
```

#### Run specific test class
```bash
pytest tests/test_project.py::TestProjectCreation -v
```

#### Run specific test
```bash
pytest tests/test_project.py::TestProjectCreation::test_create_project_success -v
```

#### Run with coverage report
```bash
pytest tests/test_project.py --cov=app/projects --cov-report=term-missing
```

**Output:**
```
Name                                       Stmts   Miss  Cover   Missing
------------------------------------------------------------------------
app/projects/__init__.py                       1      0   100%
app/projects/models.py                        79      0   100%
app/projects/project_database_manager.py      42      3    93%   40, 42, 52
app/projects/project.py                       99     58    41%   46, 58-60, 65-140
------------------------------------------------------------------------
TOTAL                                        319    105    67%
```

#### Run tests with detailed output
```bash
pytest tests/test_project.py -vv --tb=long
```

#### Run tests in parallel (faster)
```bash
pip install pytest-xdist
pytest tests/test_project.py -n auto
```

---

## CI/CD Integration

### GitHub Actions Workflow

Created `.github/workflows/run_tests.yml`:

```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11"]

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
        cache: 'pip'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run tests with pytest
      run: |
        python -m pytest tests/ -v --tb=short

    - name: Generate coverage report
      run: |
        pip install pytest-cov
        python -m pytest tests/ --cov=app --cov-report=term-missing
      continue-on-error: true
```

**What happens on every push:**
1. ✅ Tests run on Python 3.10 and 3.11
2. ✅ All dependencies installed from requirements.txt
3. ✅ Full test suite executed
4. ✅ Coverage report generated
5. ✅ Build fails if any test fails

### Viewing Results

After pushing to GitHub:
1. Go to your repository
2. Click "Actions" tab
3. See test results for each commit
4. Green checkmark = all tests passed ✅
5. Red X = some tests failed ❌

---

## Writing New Tests

### Test Structure Template

```python
class TestNewFeature:
    """Tests for new feature functionality"""
    
    def test_feature_success(self, app, test_user):
        """Test successful feature operation"""
        with app.app_context():
            # Arrange: Set up test data
            user = User.query.get(test_user)
            
            # Act: Perform the operation
            result = some_function(user, param1, param2)
            
            # Assert: Verify the outcome
            assert result is not None
            assert result.property == expected_value
    
    def test_feature_validation_error(self, app):
        """Test feature fails with invalid input"""
        with app.app_context():
            with pytest.raises(ValueError, match="expected error message"):
                some_function(invalid_param)
```

### Best Practices

1. **Follow the AAA Pattern**
   - **Arrange**: Set up test data and preconditions
   - **Act**: Execute the code being tested
   - **Assert**: Verify the results

2. **Use Descriptive Names**
   ```python
   # Good
   def test_create_project_with_empty_name_raises_error(self, app):
   
   # Bad
   def test_project1(self, app):
   ```

3. **Test One Thing at a Time**
   ```python
   # Good - tests one validation rule
   def test_project_name_min_length(self, app):
       with pytest.raises(ValueError, match="at least 3 characters"):
           handle_project_create(name='AB', ...)
   
   # Bad - tests multiple things
   def test_project_validation(self, app):
       # Tests name length AND description AND sector...
   ```

4. **Use Fixtures for Common Setup**
   ```python
   @pytest.fixture
   def authenticated_user(app):
       """Create a logged-in user"""
       with app.app_context():
           user = User(username='testuser', email='test@test.com')
           user.set_password('password')
           db.session.add(user)
           db.session.commit()
           return user
   ```

5. **Always Use `app.app_context()`**
   ```python
   # Correct
   def test_something(self, app):
       with app.app_context():
           user = User.query.get(1)  # Works!
   
   # Wrong - will crash
   def test_something(self, app):
       user = User.query.get(1)  # RuntimeError: Working outside of application context
   ```

### Adding API Tests (Future)

When ready to test HTTP endpoints:

```python
# tests/test_project_api.py
class TestProjectAPI:
    def test_create_project_endpoint(self, client, auth_headers):
        """Test POST /api/create_project"""
        response = client.post('/api/create_project', 
            json={
                'name': 'API Test Project',
                'description': 'Testing via API',
                'sector': 'Tech',
                'people_count': 3,
                'skills': ['Python']
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'project_id' in data
```

---

## FAQ

### Q: Do tests affect my production database?
**A:** No! Tests use `sqlite:///:memory:` which exists only in RAM. Your PostgreSQL production database is never touched.

### Q: Why do tests take 8-10 seconds to run?
**A:** Most time is spent:
- Importing Flask app (~2s)
- Creating database schema (~1s)
- Running 22 tests (~5s)
- Generating coverage report (~2s)

With pytest-xdist (parallel execution), this can be reduced to ~3-4 seconds.

### Q: Can I use PostgreSQL for tests instead of SQLite?
**A:** Yes, but it's slower and requires a running PostgreSQL server. SQLite in-memory is recommended for unit tests. Use PostgreSQL for integration tests.

### Q: How do I debug a failing test?
**A:** Add `--pdb` flag:
```bash
pytest tests/test_project.py::test_name -v --pdb
```
This drops you into Python debugger when a test fails.

### Q: Why use `scope='session'` for the app fixture?
**A:** Performance. Creating the Flask app is expensive. With `scope='session'`, the app is created once and reused across all tests. The database is cleaned between tests anyway.

### Q: How do I test authentication?
**A:** Use Flask-Login's `login_user()`:
```python
from flask_login import login_user

with app.test_request_context():
    login_user(user)
    # Now current_user is set
```

---

## Next Steps

### Short Term
- ✅ Complete unit tests for projects module (DONE)
- ⬜ Add API endpoint tests (`test_project_api.py`)
- ⬜ Increase business logic coverage from 41% to 80%+

### Medium Term
- ⬜ Add unit tests for auth module
- ⬜ Add unit tests for profile module
- ⬜ Create integration tests for full user workflows

### Long Term
- ⬜ Add end-to-end tests with Selenium/Playwright
- ⬜ Add performance tests (load testing with Locust)
- ⬜ Add security tests (OWASP ZAP scanning)

---

## Conclusion

This testing infrastructure provides:
- ✅ Fast, isolated unit tests (< 10 seconds)
- ✅ 67% coverage of projects module (100% of models)
- ✅ Automated CI/CD testing on every push
- ✅ Foundation for adding more test types
- ✅ Confidence in refactoring and adding features

**Test early, test often, deploy confidently!** 🚀
