# 🧪 Test Suite Documentation

This directory contains the comprehensive test suite for the MoneyFlowV2 application.

## 📁 Test Structure

```
tests/
├── __init__.py                 # Python package initialization
├── conftest.py                 # Pytest configuration and shared fixtures
├── test_imports.py            # Basic import verification tests
├── test_auto_recovery.py      # Auto-recovery mechanism tests
├── integration/               # Integration tests
│   ├── test_database_crud.py  # Comprehensive CRUD tests for all SQLite tables
│   ├── test_core_components.py # Core component integration tests
│   └── test_schema_manager.py # SchemaManager live database tests
├── e2e/                      # End-to-end tests
│   └── test_workflow.py      # Complete workflow testing
├── test_core/                # Core module unit tests
├── test_models/              # Data model unit tests
├── test_ui/                  # UI component tests
├── test_utils/               # Utility function tests
└── fixtures/                 # Test data and fixtures
```

## 🎯 Test Categories

### **Integration Tests** (`tests/integration/`)
- **`test_database_crud.py`**: Tests CRUD operations for all 7 SQLite tables
- **`test_core_components.py`**: Tests integration between ExcelProcessor, MongoCollectionManager, and DataIngestionEngine
- **`test_schema_manager.py`**: Live tests for SchemaManager with real database operations

### **End-to-End Tests** (`tests/e2e/`)
- **`test_workflow.py`**: Tests complete application workflow from UI to database

### **Unit Tests**
- **`test_imports.py`**: Verifies all core modules can be imported
- **`test_auto_recovery.py`**: Tests the auto-recovery mechanism for terminal blocking

## 🚀 Running Tests

### Run All Tests
```bash
python -m pytest tests/
```

### Run Specific Test Categories
```bash
# Integration tests only
python -m pytest tests/integration/

# E2E tests only
python -m pytest tests/e2e/

# Specific test file
python -m pytest tests/integration/test_database_crud.py
```

### Run with Coverage
```bash
python -m pytest tests/ --cov=src --cov-report=html
```

## 📊 Test Coverage

The test suite covers:

- ✅ **Database Operations**: All SQLite table CRUD operations
- ✅ **Core Components**: ExcelProcessor, MongoCollectionManager, DataIngestionEngine
- ✅ **Schema Management**: Complete schema lifecycle (create, read, update, delete)
- ✅ **Integration**: Component interaction and data flow
- ✅ **E2E Workflows**: Complete application workflows
- ✅ **Error Handling**: Edge cases and error conditions
- ✅ **Data Validation**: Input validation and sanitization

## 🔧 Test Configuration

- **Pytest Configuration**: `pytest.ini` in project root
- **Test Database**: Uses separate test SQLite database
- **MongoDB**: Uses test collections (automatically cleaned up)
- **Fixtures**: Shared test data and setup in `conftest.py`

## 🧹 Test Cleanup

All tests automatically clean up after themselves:
- Test databases are reset
- Test collections are dropped
- Temporary files are removed
- No test data persists between test runs

## 📝 Adding New Tests

### For New Features
1. Create unit tests in appropriate category folder
2. Add integration tests if component interaction is involved
3. Add E2E tests for complete workflows
4. Update this README with new test descriptions

### Test Naming Convention
- Unit tests: `test_<function_name>.py`
- Integration tests: `test_<component>_integration.py`
- E2E tests: `test_<workflow_name>.py`

## 🚨 Important Notes

- **Virtual Environment**: Always run tests in the project's virtual environment
- **Database State**: Tests modify database state - never run on production
- **Dependencies**: Ensure all test dependencies are installed (`requirements-dev.txt`)
- **Clean State**: Tests assume clean database state - run cleanup if needed

## 🔍 Debugging Tests

### Verbose Output
```bash
python -m pytest tests/ -v -s
```

### Stop on First Failure
```bash
python -m pytest tests/ -x
```

### Run Specific Test Function
```bash
python -m pytest tests/integration/test_database_crud.py::test_schema_definitions_crud
```

## 📈 Test Metrics

- **Total Tests**: 15+ test functions
- **Coverage Target**: 90%+ code coverage
- **Execution Time**: <30 seconds for full suite
- **Database Tables Tested**: 7 SQLite tables
- **Components Tested**: 5 core components

