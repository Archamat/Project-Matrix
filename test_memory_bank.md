# Existing Tests Documentation

> **Status:** This is a living document that tracks all tests implemented in Project Matrix.
> **Last Updated:** December 1, 2025
> **Current Test Count:** 2 (Static Analysis + Pre-commit Hooks) + Profile Module Unit Tests

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

#### How It Works
Once installed, pre-commit will:
1. Run automatically before each `git commit`
2. Check and fix files being committed
3. Prevent commit if critical issues found
4. Auto-fix issues when possible

#### Manual Run
```bash
# Run on all files
pre-commit run --all-files

# Run on specific files
pre-commit run --files app/auth/models.py

# Skip hooks for emergency commits (use sparingly)
git commit --no-verify
```

---

## Unit Testing Status

### ✅ Profile Module Tests Implemented

The `tests/` directory now contains comprehensive test files for the profile module.

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures and test configuration
├── test_profile_models.py   # Skill and UserSkill model tests
├── test_profile_database_manager.py  # Database operations tests
├── test_profile_handlers.py # Business logic handler tests
├── test_profile_routes.py   # View route tests
└── test_profile_api.py       # API endpoint tests
```

### Testing Infrastructure Status

| Component | Status | Notes |
|-----------|--------|-------|
| Test Directory | ✅ Created | `/tests/` exists |
| Test Files | ✅ Created | Profile module tests implemented |
| `conftest.py` | ✅ Created | Shared fixtures and test configuration |
| `pytest.ini` | ⚠️ Optional | Can be added for custom pytest config |
| CI/CD Pipeline | ✅ Configured | `.github/workflows/` ready |
| Dependencies | ⚠️ Check Needed | Verify pytest is in requirements.txt |
| Pylint | ✅ Active | Running on CI/CD |
| Pre-commit | ⚠️ Configured | Needs local installation |

---

## Planned Test Structure

When unit tests are implemented, they should follow this structure:

```
tests/
├── __init__.py              # Make tests a package
├── conftest.py              # Shared fixtures and configuration
├── test_auth.py             # Authentication module tests
├── test_profile.py          # Profile module tests
├── test_projects.py         # Projects module tests
├── test_search.py           # Search functionality tests
├── test_dashboard.py        # Dashboard tests
├── test_filter.py           # Filter functionality tests
└── test_integration.py      # Integration/E2E tests
```

---

## Test Coverage Needed by Module

### 🔴 Authentication Module (`app/auth/`)

**Status:** Not tested
**Priority:** HIGH (security-critical)

**Files requiring tests:**
- `models.py` - User model, password hashing
- `auth.py` - Login/logout handlers
- `auth_database_manager.py` - User CRUD operations
- `routes.py` - Auth route endpoints
- `api.py` - Auth API endpoints
- `forms.py` - Registration/login form validation

**Recommended test cases:**
- User registration (valid/invalid inputs)
- Duplicate username/email handling
- Password hashing verification
- Login success/failure scenarios
- Logout functionality
- Session management

---

### ✅ Profile Module (`app/profile/`)

**Status:** TESTED
**Priority:** HIGH
**Test Files:** `tests/test_profile_*.py` (5 test files)

**Files tested:**
- ✅ `models.py` - Skill and UserSkill models (test_profile_models.py)
- ✅ `profile.py` - Profile handlers (test_profile_handlers.py)
- ✅ `profile_database_manager.py` - Profile CRUD (test_profile_database_manager.py)
- ✅ `routes.py` - Profile routes (test_profile_routes.py)
- ✅ `api.py` - Profile API endpoints (test_profile_api.py)

**Test coverage:**

#### Models (`test_profile_models.py`)
- ✅ Skill model creation and uniqueness
- ✅ UserSkill model creation and relationships
- ✅ Unique constraint on user-skill pairs
- ✅ Optional fields (level, years)

#### Database Manager (`test_profile_database_manager.py`)
- ✅ `get_user_by_username` - existing and nonexistent users
- ✅ `update_user_profile` - success, partial updates, duplicate validation
- ✅ `update_avatar` - success and overwrite scenarios
- ✅ `get_or_create_skill` - get existing and create new
- ✅ `add_user_skill` - success, duplicate prevention, skill creation
- ✅ `get_user_skill` - authorization checks
- ✅ `delete_user_skill` - deletion and skill preservation

#### Handlers (`test_profile_handlers.py`)
- ✅ `handle_profile` - user data and participated projects
- ✅ `handle_update_profile` - validation, sanitization, duplicates
- ✅ `handle_avatar_upload` - success and error cases
- ✅ `handle_skill_add` - validation (name, level, years), duplicates
- ✅ `handle_skill_delete` - success, authorization, nonexistent skills

#### Routes (`test_profile_routes.py`)
- ✅ Authentication requirements for all routes
- ✅ View own profile (`/profile`)
- ✅ View other user profiles (`/u/<username>`)
- ✅ Avatar upload with file validation
- ✅ Profile update with form data
- ✅ Skill add/delete with validation

#### API (`test_profile_api.py`)
- ✅ JSON and form data support
- ✅ Proper HTTP status codes
- ✅ Error handling and messages
- ✅ Authentication requirements
- ✅ All CRUD operations for skills
- ✅ Avatar upload with presigned URLs

**Total Test Cases:** ~80+ individual test methods covering:
- Model relationships and constraints
- Database operations (CRUD)
- Business logic validation
- Route authentication and authorization
- API endpoint responses
- Error handling scenarios

---

### 🔴 Projects Module (`app/projects/`)

**Status:** Not tested
**Priority:** HIGH (core feature)

**Files requiring tests:**
- `models.py` - Project, Application, Task, ChatMessage, etc.
- `project.py` - Project business logic
- `project_database_manager.py` - Project CRUD
- `routes.py` - Project routes
- `api.py` - Project API endpoints
- `forms.py` - Project form validation

**Recommended test cases:**
- Create project (valid/invalid data)
- Project name validation (length, special chars)
- View project list/details
- Apply to project
- View applicants (authorization)
- Accept/reject applications
- Project creator permissions
- Task management (CRUD)
- Chat messages
- Project links and notes

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


## Coverage Goals

| Module | Target Coverage | Current | Status |
|--------|----------------|---------|--------|
| Static Analysis | 100% | 100% | ✅ Active |
| Pre-commit Hooks | 100% | 100% | ⚠️ Configured |
| auth | 90%+ | 0% | ❌ Not started |
| profile | 85%+ | ~85%+ | ✅ Implemented |
| projects | 90%+ | 0% | ❌ Not started |
| search | 80%+ | 0% | ❌ Not started |
| dashboard | 75%+ | 0% | ❌ Not started |
| filter | 70%+ | 0% | ❌ Not started |

---

## Running Tests

### Unit Tests (Profile Module)

```bash
# Install pytest if not already installed
pip install pytest pytest-flask

# Run all profile tests
pytest tests/test_profile_*.py

# Run specific test file
pytest tests/test_profile_models.py

# Run with verbose output
pytest tests/test_profile_*.py -v

# Run with coverage (if pytest-cov installed)
pytest tests/test_profile_*.py --cov=app.profile --cov-report=html

# Run specific test
pytest tests/test_profile_models.py::TestSkillModel::test_create_skill
```

### Pre-commit (Current)

```bash
# First-time setup
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files

# Runs automatically on git commit
git commit -m "Your message"
```

## Test Writing Guidelines

### Naming Conventions

- **Test files:** `test_<module>.py`
- **Test classes:** `Test<Feature>`
- **Test functions:** `test_<feature>_<scenario>`

### Example Test Structure

```python
# tests/test_auth.py
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
        user = User.query.filter_by(username='testuser').first()
        assert user is not None
        assert user.email == 'test@example.com'
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

### Current CI/CD Setup

**Pylint Workflow** (`.github/workflows/static_code_analysis.yml`)
- ✅ Runs on push and pull requests
- ✅ Tests Python 3.10 and 3.11
- ✅ Excludes temp directories
- ✅ Continues on errors (warnings only)

**Status:** Fully operational

---

## Contributing

### Before Committing

1. **Install pre-commit** (if not done)
   ```bash
   pip install pre-commit
   pre-commit install
   ```

2. **Run pre-commit manually** (first time)
   ```bash
   pre-commit run --all-files
   ```

3. **Commit as normal** - hooks run automatically
   ```bash
   git add .
   git commit -m "Your message"
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
| 2025-12-01 | System | Implemented comprehensive profile module tests (5 test files, 80+ test cases) |
| 2025-11-30 | System | Added static analysis and pre-commit documentation |
| 2025-11-30 | System | Initial documentation - no unit tests exist yet |

---

**NOTE:** This document should be updated every time new tests are added or removed. Treat it as the single source of truth for test coverage across the team.
