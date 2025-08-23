# MoneyFlowV2 - Data Ingestion App Project Structure

```
MoneyFlowV2/
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schema_definition.py
│   │   ├── ingestion_result.py
│   │   ├── validation_result.py
│   │   └── audit_models.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── schema_manager.py
│   │   ├── ai_processor.py
│   │   ├── mongo_manager.py
│   │   ├── excel_processor.py
│   │   ├── data_ingestion_engine.py
│   │   ├── column_mapping_manager.py
│   │   ├── audit_logger.py
│   │   ├── rollback_manager.py
│   │   └── batch_import_manager.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── controllers/
│   │   │   ├── __init__.py
│   │   │   ├── main_window_controller.py
│   │   │   ├── schema_creation_controller.py
│   │   │   └── history_controller.py
│   │   └── views/
│   │       ├── __init__.py
│   │       ├── main_window.py
│   │       ├── schema_creation_modal.py
│   │       └── history_window.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── database_utils.py
│   │   ├── file_utils.py
│   │   └── validation_utils.py
│   └── config/
│       ├── __init__.py
│       ├── settings.py
│       └── database_config.py
├── tests/
│   ├── __init__.py
│   ├── test_models/
│   │   ├── __init__.py
│   │   ├── test_schema_definition.py
│   │   ├── test_ingestion_result.py
│   │   ├── test_validation_result.py
│   │   └── test_audit_models.py
│   ├── test_core/
│   │   ├── __init__.py
│   │   ├── test_schema_manager.py
│   │   ├── test_ai_processor.py
│   │   ├── test_mongo_manager.py
│   │   ├── test_excel_processor.py
│   │   ├── test_data_ingestion_engine.py
│   │   ├── test_column_mapping_manager.py
│   │   ├── test_audit_logger.py
│   │   ├── test_rollback_manager.py
│   │   └── test_batch_import_manager.py
│   ├── test_ui/
│   │   ├── __init__.py
│   │   ├── test_controllers/
│   │   │   ├── __init__.py
│   │   │   ├── test_main_window_controller.py
│   │   │   ├── test_schema_creation_controller.py
│   │   │   └── test_history_controller.py
│   │   └── test_views/
│   │       ├── __init__.py
│   │       ├── test_main_window.py
│   │       ├── test_schema_creation_modal.py
│   │       └── test_history_window.py
│   ├── test_utils/
│   │   ├── __init__.py
│   │   ├── test_database_utils.py
│   │   ├── test_file_utils.py
│   │   └── test_validation_utils.py
│   ├── fixtures/
│   │   ├── __init__.py
│   │   ├── sample_excel_files/
│   │   │   ├── customer_data.xlsx
│   │   │   ├── sales_data.xlsx
│   │   │   └── invalid_data.xlsx
│   │   ├── mock_schemas.py
│   │   └── test_data.py
│   └── conftest.py
├── data/
│   └── templates.db (SQLite database - created at runtime)
├── docs/
│   ├── README.md
│   ├── SETUP.md
│   ├── API_REFERENCE.md
│   └── ARCHITECTURE.md
├── scripts/
│   ├── setup_database.py
│   ├── run_tests.py
│   └── build_app.py
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
├── .gitignore
├── setup.py
└── main.py
```

## Directory Descriptions

### `/src/` - Source Code
- **`models/`** - Data classes and model definitions
- **`core/`** - Core business logic and processing engines
- **`ui/`** - User interface controllers and views
- **`utils/`** - Utility functions and helpers
- **`config/`** - Configuration management

### `/tests/` - Unit Tests
- **`test_models/`** - Tests for data models
- **`test_core/`** - Tests for core business logic
- **`test_ui/`** - Tests for UI components
- **`test_utils/`** - Tests for utility functions
- **`fixtures/`** - Test data and mock objects

### `/data/` - Data Storage
- SQLite database file (created at runtime)

### `/docs/` - Documentation
- Setup guides, API reference, architecture docs

### `/scripts/` - Utility Scripts
- Database setup, testing, and build scripts
