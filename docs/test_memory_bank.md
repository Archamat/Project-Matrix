# Existing Tests Documentation

> **Status:** This is a living document that tracks all tests implemented in Project Matrix.  
> **Last Updated:** January 2026  
> **Current Test Count:** 94+ unit tests + Static Analysis + Pre-commit Hooks  
> **Test Status:** ✅ ALL TESTS PASSING

---

## Purpose

This document serves as a **test memory bank** for the development team to:
- Track what has been tested and what hasn't
- Avoid duplicate test implementation
- Identify testing gaps
- Provide quick reference for test coverage
- Guide new team members on testing status

---

## Automated Testing & Code Quality

### ✅ Static Code Analysis (Pylint)

**Status:** ACTIVE  
**Location:** `.github/workflows/static_code_analysis.yml`  
**Configuration:** `.pylintrc`

#### What It Does
- Runs automatically on every push and pull request
- Analyzes Python code for errors, bugs, and style issues
- Tests against Python 3.10 and 3.11

#### Excluded Directories
```
migrations/, venv/, env/, .venv/, __pycache__/
.pytest_cache/, .ruff_cache/, .coverage, build/
dist/, .eggs/, .tox/
```

#### Disabled Checks
- `C0114` - missing-module-docstring
- `C0115` - missing-class-docstring  
- `C0116` - missing-function-docstring

#### Configuration Details
```ini
# .pylintrc
- Max line length: 100 characters
- Max arguments: 7
- Max attributes: 10
- Minimum similarity lines: 4
- Multi-process: 4 jobs
```

### ✅ Pre-commit Hooks (Ruff)

**Status:** CONFIGURED (requires installation)  
**Location:** `.pre-commit-config.yaml`  
**Tool:** Ruff (fast linter + formatter)

#### What It Does
Runs automatically before each commit to:
- Remove trailing whitespace
- Fix file endings
- Validate YAML files
- Check for large files (>5MB)
- Lint Python code with Ruff
- Auto-format Python code

#### Hooks Configured

1. **Basic File Checks**
   - `trailing-whitespace` - Remove trailing spaces
   - `end-of-file-fixer` - Ensure files end with newline
   - `check-yaml` - Validate YAML syntax
   - `check-added-large-files` - Prevent large file commits

2. **Ruff Linter & Formatter**
   - `ruff` - Fast Python linter with auto-fix
   - `ruff-format` - Fast Python formatter (Black-compatible)

#### Excluded Directories
```
migrations/, venv/, env/, .venv/, __pycache__/
.pytest_cache/, .ruff_cache/, .coverage.*
build/, dist/, .eggs/, .tox/
```

#### Installation & Setup

```bash
# Install pre-commit
pip install pre-commit

# Install the git hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files

# Update hooks to latest versions
pre-commit autoupdate
```

---

## Unit Testing Status

### Current Test Structure

```
tests/
├── __init__.py                    # Test package initialization
├── conftest.py                    # Shared fixtures (17 fixtures)
├── test_auth.py                   # Authentication module tests (38 tests)
├── test_hello_world.py            # Basic sanity tests
├── test_profile_api.py            # Profile API tests
├── test_profile_database_manager.py  # Profile DB manager tests
├── test_profile_handlers.py       # Profile handler tests
├── test_profile_models.py         # Profile model tests
├── test_profile_routes.py         # Profile route tests
├── test_projects.py               # Projects module tests (56 tests)
└── __pycache__/
```

### Testing Infrastructure Status

| Component | Status | Notes |
|-----------|--------|-------|
| Test Directory | ✅ Created | `/tests/` exists |
| Test Files | ✅ Created | Multiple test modules |
| `conftest.py` | ✅ Created | 17 comprehensive fixtures |
| `pytest.ini` | ✅ Created | Pytest configuration |
| CI/CD Pipeline | ✅ Created | `.github/workflows/tests.yml` |
| Dependencies | ✅ Installed | pytest, pytest-flask, pytest-cov |
| Pylint | ✅ Active | Running on CI/CD |
| Pre-commit | ⚠️ Configured | Needs local installation |

---

## Test Coverage by Module

### ✅ Authentication Module (`app/auth/`) - FULLY TESTED

**Status:** ✅ COMPLETE  
**Location:** `tests/test_auth.py`  
**Test Count:** 38 test cases  
**Priority:** HIGH (security-critical)

**Files tested:**
- ✅ `models.py` - User model, password hashing, unique constraints, avatar properties
- ✅ `auth.py` - Login/register/logout handlers with error handling
- ✅ `auth_database_manager.py` - User CRUD operations (create, get by username)
- ✅ `routes.py` - Auth route endpoints (GET /login, GET /register)
- ✅ `api.py` - Auth API endpoints (POST /api/login, /api/register, /api/logout)
- ✅ `forms.py` - Registration/login form validation (WTForms)

**Test Classes:**

1. **TestUserModel** (7 tests)
   - `test_user_creation` - User creation with valid data
   - `test_password_hashing` - Password hash format verification
   - `test_password_checking` - Password verification (correct/incorrect)
   - `test_user_unique_username` - Unique username constraint
   - `test_user_unique_email` - Unique email constraint
   - `test_avatar_presigned_property` - Avatar presigned URL generation
   - `test_avatar_presigned_none_when_no_url` - Avatar None handling

2. **TestAuthDatabaseManager** (4 tests)
   - `test_create_user_success` - Successful user creation
   - `test_create_user_duplicate_username` - Duplicate username prevention
   - `test_get_user_by_username_exists` - User lookup (exists)
   - `test_get_user_by_username_not_exists` - User lookup (not exists)

3. **TestAuthHandlers** (11 tests)
   - `test_handle_login_success` - Successful login
   - `test_handle_login_missing_username` - Login validation (missing username)
   - `test_handle_login_missing_password` - Login validation (missing password)
   - `test_handle_login_invalid_username` - Login validation (invalid username)
   - `test_handle_login_invalid_password` - Login validation (invalid password)
   - `test_handle_register_success` - Successful registration
   - `test_handle_register_missing_username` - Register validation (missing username)
   - `test_handle_register_missing_email` - Register validation (missing email)
   - `test_handle_register_missing_password` - Register validation (missing password)
   - `test_handle_register_duplicate_username` - Register validation (duplicate)
   - `test_handle_logout_success` - Successful logout

4. **TestAuthAPI** (7 tests)
   - `test_api_login_success` - API login endpoint (200)
   - `test_api_login_missing_data` - API login validation (400)
   - `test_api_login_invalid_credentials` - API login invalid credentials (400)
   - `test_api_register_success` - API register endpoint (201)
   - `test_api_register_missing_data` - API register validation (400)
   - `test_api_register_duplicate_username` - API register duplicate (400)
   - `test_api_logout_success` - API logout endpoint (200)

5. **TestAuthRoutes** (2 tests)
   - `test_login_route_get` - GET /login route rendering
   - `test_register_route_get` - GET /register route rendering

6. **TestAuthForms** (7 tests)
   - `test_login_form_valid` - LoginForm valid data
   - `test_login_form_missing_username` - LoginForm validation (missing username)
   - `test_login_form_missing_password` - LoginForm validation (missing password)
   - `test_registration_form_valid` - RegistrationForm valid data
   - `test_registration_form_missing_username` - RegistrationForm validation
   - `test_registration_form_invalid_email` - RegistrationForm validation
   - `test_registration_form_password_mismatch` - RegistrationForm validation

---

### ✅ Profile Module (`app/profile/`) - TESTED

**Status:** ✅ COMPLETE  
**Location:** `tests/test_profile_*.py`  
**Priority:** HIGH

**Test Files:**
- `test_profile_api.py` - Profile API endpoint tests
- `test_profile_database_manager.py` - Profile DB manager tests
- `test_profile_handlers.py` - Profile handler tests
- `test_profile_models.py` - Profile model tests
- `test_profile_routes.py` - Profile route tests

**Files tested:**
- ✅ `models.py` - Skill, UserSkill, Demo models
- ✅ `profile.py` - Profile handlers
- ✅ `profile_database_manager.py` - Profile CRUD operations
- ✅ `routes.py` - Profile routes
- ✅ `api.py` - Profile API endpoints

---

### ✅ Projects Module (`app/projects/`) - FULLY TESTED

**Status:** ✅ COMPLETE  
**Location:** `tests/test_projects.py`  
**Test Count:** 56 test cases across 12 test classes  
**Test Runtime:** ~22 seconds  
**Priority:** HIGH (core feature)

**Files tested:**
- ✅ `models.py` - Project, Application, Task, ChatMessage, ProjectLink, ProjectNote
- ✅ `project.py` - Project business logic
- ✅ `project_database_manager.py` - Project CRUD operations
- ✅ `routes.py` - Project route endpoints
- ✅ `api.py` - Project API endpoints
- ✅ `forms.py` - Project form validation

**Test Classes:**

1. **TestProjectModel** (4 tests)
   - `test_project_creation` - Creating project with valid data
   - `test_project_to_dict` - Project serialization
   - `test_project_skills_parsing` - Skills parsing to list
   - `test_project_without_skills` - Project without skills

2. **TestApplicationModel** (3 tests)
   - `test_application_creation` - Creating application
   - `test_application_relationship_with_project` - Project relationship
   - `test_application_relationship_with_user` - User relationship

3. **TestTaskModel** (3 tests)
   - `test_task_creation` - Creating tasks
   - `test_task_toggle_completion` - Toggle task status
   - `test_task_relationship_with_project` - Project relationship

4. **TestChatMessageModel** (2 tests)
   - `test_chat_message_creation` - Creating messages
   - `test_chat_message_relationships` - Relationships

5. **TestProjectLinkModel** (2 tests)
   - `test_project_link_creation` - Creating links
   - `test_project_link_relationship` - Project relationship

6. **TestProjectNoteModel** (2 tests)
   - `test_project_note_creation` - Creating notes
   - `test_project_note_with_title` - Notes with titles

7. **TestProjectDatabaseManager** (10 tests)
   - `test_create_project` - Project creation via manager
   - `test_create_project_invalid_creator` - Invalid creator handling
   - `test_get_project_by_id` - Retrieve by ID
   - `test_get_project_by_id_not_found` - Not found handling
   - `test_get_all_projects` - Retrieve all projects
   - `test_apply_to_project` - Submit application
   - `test_apply_to_project_invalid_project` - Invalid project
   - `test_add_element_to_project` - Add tasks/links/notes
   - `test_add_element_to_invalid_project` - Invalid project handling
   - `test_delete_element_from_project` - Delete elements

8. **TestProjectBusinessLogic** (9 tests)
   - `test_handle_project_create_success` - Successful creation
   - `test_handle_project_create_with_other_skill` - Custom skills
   - `test_handle_project_create_name_too_short` - Name validation
   - `test_handle_project_create_empty_name` - Empty name handling
   - `test_handle_apply_project_success` - Successful application
   - `test_get_project_applicants_as_creator` - View applicants as creator
   - `test_get_project_applicants_not_creator` - Authorization check
   - `test_get_project_applicants_invalid_project` - Invalid project
   - `test_get_project_by_id_success` - Retrieve project

9. **TestProjectForms** (2 tests)
   - `test_project_creation_form_valid_data` - Valid form data
   - `test_application_form_valid_data` - Valid application form

10. **TestProjectAPI** (7 tests)
    - `test_get_projects_api` - GET /api/projects
    - `test_get_project_by_id_api` - GET /api/project/<id>
    - `test_get_project_by_id_api_not_found` - 404 handling
    - `test_create_project_api_success` - POST /api/create_project
    - `test_create_project_api_invalid_name` - Invalid data handling
    - `test_apply_project_api_success` - POST /api/apply/<id>
    - `test_get_project_applicants_api_as_creator` - GET applicants

11. **TestProjectRoutes** (6 tests)
    - `test_project_detail_route` - GET /project/<id>
    - `test_create_project_route_authenticated` - Authenticated access
    - `test_create_project_route_unauthenticated` - Redirect to login
    - `test_apply_project_route_authenticated` - Apply route access
    - `test_project_applicants_route_as_creator` - Applicants route
    - `test_project_gui_route` - Project GUI route

12. **TestCascadeDeletes** (5 tests)
    - `test_delete_project_cascades_to_applications` - Application cascade
    - `test_delete_project_cascades_to_tasks` - Task cascade
    - `test_delete_project_cascades_to_messages` - Message cascade
    - `test_delete_project_cascades_to_links` - Link cascade
    - `test_delete_project_cascades_to_notes` - Note cascade

---

### 🔴 Search Module (`app/search/`)

**Status:** Not tested  
**Priority:** MEDIUM

**Recommended test cases:**
- Search users by username
- Search projects by name/description
- Search by skills
- Empty search query handling
- Special characters in search
- Search result pagination

---

### 🔴 Dashboard Module (`app/dashboard/`)

**Status:** Not tested  
**Priority:** MEDIUM

**Recommended test cases:**
- View dashboard (authenticated)
- Display user's projects
- Display applied projects
- Recent projects display
- Filter integration

---

### 🔴 Filter Module (`app/filter/`)

**Status:** Not tested  
**Priority:** LOW

**Recommended test cases:**
- Filter by sector
- Filter by skills
- Filter by people count
- Multiple filters combined

---

## Test Fixtures (conftest.py)

The following fixtures are available for all tests:

| Fixture | Description |
|---------|-------------|
| `app` | Flask test application with in-memory SQLite database |
| `db` | Database instance |
| `client` | Test HTTP client |
| `runner` | CLI test runner |
| `test_user` | Primary test user |
| `test_user_2` | Secondary test user |
| `other_user` | Another test user |
| `sample_user` | Sample user for auth tests |
| `auth_client` | Authenticated HTTP client |
| `authenticated_client` | Authenticated client with fresh session |
| `test_project` | Sample project |
| `test_application` | Sample application |
| `test_task` | Sample task |
| `test_chat_message` | Sample chat message |
| `test_project_link` | Sample project link |
| `test_project_note` | Sample project note |
| `test_skill` | Sample skill |
| `test_user_skill` | Sample user skill |
| `user` | Alias for test_user |
| `skill` | Alias for test_skill |

---

## Coverage Goals

| Module | Target Coverage | Current | Tests | Status |
|--------|----------------|---------|-------|--------|
| Static Analysis | 100% | 100% | Pylint CI | ✅ Active |
| Pre-commit Hooks | 100% | 100% | Ruff | ⚠️ Configured |
| auth | 90%+ | 90%+ | 38 | ✅ Complete |
| profile | 85%+ | 85%+ | Multiple | ✅ Complete |
| projects | 90%+ | 90%+ | 56 | ✅ Complete |
| search | 80%+ | 0% | 0 | ❌ Not started |
| dashboard | 75%+ | 0% | 0 | ❌ Not started |
| filter | 70%+ | 0% | 0 | ❌ Not started |

---

## Running Tests

### All Tests

```bash
# Run all tests
pytest -v

# Run with coverage
pytest -v --cov=app --cov-report=html

# Run with verbose output and coverage
pytest -v --cov=app --cov-report=term-missing
```

### Module-Specific Tests

```bash
# Auth tests
pytest tests/test_auth.py -v

# Profile tests
pytest tests/test_profile_*.py -v

# Projects tests
pytest tests/test_projects.py -v

# Run specific test class
pytest tests/test_projects.py::TestProjectModel -v

# Run specific test
pytest tests/test_auth.py::TestUserModel::test_user_creation -v
```

### Pre-commit

```bash
# First-time setup
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files

# Runs automatically on git commit
git commit -m "Your message"
```

---

## Test Writing Guidelines

### Naming Conventions

- **Test files:** `test_<module>.py`
- **Test classes:** `Test<Feature>`
- **Test functions:** `test_<feature>_<scenario>`

### Example Test Structure

```python
# tests/test_example.py
import pytest
from app.auth.models import User

class TestUserAuthentication:
    """Tests for user authentication"""
    
    def test_user_registration_success(self, app, client):
        """Test successful user registration with valid data"""
        # Arrange
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'SecurePass123'
        }
        
        # Act
        response = client.post('/register', data=user_data)
        
        # Assert
        assert response.status_code == 302  # Redirect on success
```

### Best Practices

1. **Use AAA Pattern:** Arrange, Act, Assert
2. **One assertion per test** (when possible)
3. **Descriptive test names** - explain what and why
4. **Test both success and failure paths**
5. **Mock external services** (S3, APIs, etc.)
6. **Clean up after tests** (use fixtures with teardown)
7. **Keep tests independent** - no order dependencies

---

## Continuous Integration

### CI/CD Workflows

**Pylint Workflow** (`.github/workflows/static_code_analysis.yml`)
- ✅ Runs on push and pull requests
- ✅ Tests Python 3.10 and 3.11
- ✅ Excludes temp directories

**Tests Workflow** (`.github/workflows/tests.yml`)
- ✅ Runs on push and pull requests
- ✅ Tests Python 3.10 and 3.11
- ✅ Runs pytest with coverage
- ✅ Uploads coverage reports to Codecov

---

## Contributing

### Before Committing

1. **Install pre-commit** (if not done)
   ```bash
   pip install pre-commit
   pre-commit install
   ```

2. **Run tests locally**
   ```bash
   pytest -v
   ```

3. **Run pre-commit manually** (first time)
   ```bash
   pre-commit run --all-files
   ```

### When Adding New Tests

1. **Create test file** in `tests/` directory
2. **Follow naming conventions** above
3. **Add test cases** with clear docstrings
4. **Run tests locally** before pushing
5. **Update this document** with test details

---

## References

- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Detailed testing methodology
- [pre_commit_install.md](pre_commit_install.md) - Pre-commit setup instructions
- [pytest documentation](https://docs.pytest.org/)
- [Ruff documentation](https://docs.astral.sh/ruff/)
- [Pylint documentation](https://pylint.readthedocs.io/)

---

## Update History

| Date | Author | Change |
|------|--------|--------|
| 2026-01-16 | System | Consolidated duplicate documentation from branch merges |
| 2026-01-16 | System | Updated conftest.py fixtures list (17 fixtures) |
| 2025-12 | System | Added profile module tests |
| 2025-12 | System | Implemented projects module tests (56 test cases) |
| 2025-12 | System | Implemented auth module tests (38 test cases) |
| 2025-11-30 | System | Added static analysis and pre-commit documentation |
| 2025-11-30 | System | Initial documentation |

---

**NOTE:** This document should be updated every time new tests are added or removed. Treat it as the single source of truth for test coverage across the team.
