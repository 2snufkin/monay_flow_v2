# 🛠️ Developer Setup Guide

This guide will help you set up the MoneyFlowV2 development environment and get started with development.

## 📋 **Prerequisites**

### **Required Software**
- **Python 3.11+** - [Download from python.org](https://python.org/downloads/)
- **Git** - [Download from git-scm.com](https://git-scm.com/downloads)
- **VS Code** (recommended) - [Download from code.visualstudio.com](https://code.visualstudio.com/)

### **Required Accounts**
- **OpenAI API Key** - [Get from platform.openai.com](https://platform.openai.com/api-keys)
- **MongoDB Atlas Account** - [Sign up at mongodb.com/atlas](https://mongodb.com/atlas)

## 🚀 **Quick Setup**

### **1. Clone the Repository**
```bash
git clone <repository-url>
cd MoneyFlowV2
```

### **2. Create Virtual Environment**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
```

### **3. Install Dependencies**
```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

### **4. Set Up Environment Variables**
```bash
# Copy environment template
cp env.example .env

# Edit .env with your actual values
notepad .env
```

**Required Environment Variables:**
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1-nano

# MongoDB Configuration
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/excel_imports

# Application Configuration
ENVIRONMENT=development
LOG_LEVEL=DEBUG
```

### **5. Initialize Database**
```bash
python scripts/setup/init_database.py
```

### **6. Run Tests**
```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### **7. Launch Application**
```bash
python main.py
```

## 🏗️ **Project Structure**

```
MoneyFlowV2/
├── src/                    # Source code
│   ├── core/              # Core business logic
│   │   ├── ai_processor.py      # OpenAI integration
│   │   ├── excel_processor.py   # Excel file processing
│   │   ├── mongo_collection_manager.py  # MongoDB operations
│   │   ├── data_ingestion_engine.py     # Main pipeline
│   │   └── schema_manager.py    # Schema management
│   ├── ui/                # User interface
│   │   └── main_window.py       # Main application window
│   ├── models/            # Data models
│   │   └── schema_definition.py # Schema data structures
│   ├── config/            # Configuration
│   │   ├── settings.py           # Application settings
│   │   ├── database_config.py    # Database configuration
│   │   ├── logging_config.py     # Logging setup
│   │   └── paths.py              # Path management
│   └── utils/             # Utilities
│       └── validation.py         # Input validation
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── e2e/               # End-to-end tests
├── docs/                  # Documentation
├── scripts/               # Utility scripts
└── requirements.txt       # Dependencies
```

## 🔧 **Development Workflow**

### **1. Code Style**
The project uses several tools to maintain code quality:

```bash
# Format code with Black
black src/ tests/

# Sort imports with isort
isort src/ tests/

# Check code style with flake8
flake8 src/ tests/

# Type checking with mypy
mypy src/
```

### **2. Pre-commit Hooks**
Install pre-commit hooks for automatic code formatting:

```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install
```

### **3. Testing Strategy**
- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test component interactions
- **E2E Tests**: Test complete workflows
- **Coverage Target**: 90%+ code coverage

### **4. Database Development**
- **SQLite**: Used for development and testing
- **MongoDB**: Used for production data storage
- **Migrations**: Automatic schema updates

## 🧪 **Testing**

### **Running Tests**
```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/unit/           # Unit tests only
python -m pytest tests/integration/    # Integration tests only
python -m pytest tests/e2e/            # End-to-end tests only

# Run specific test file
python -m pytest tests/unit/test_schema_manager.py

# Run specific test function
python -m pytest tests/unit/test_schema_manager.py::test_create_schema

# Run with verbose output
python -m pytest tests/ -v -s

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### **Test Data**
- Tests use separate test databases
- Test data is automatically cleaned up
- Fixtures are available in `tests/fixtures/`

### **Writing Tests**
Follow these guidelines:
- Test one thing per test function
- Use descriptive test names
- Arrange-Act-Assert pattern
- Mock external dependencies
- Test both success and failure cases

## 🐛 **Debugging**

### **Logging**
The application uses structured logging:

```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical error")
```

### **Debug Mode**
Enable debug mode in `.env`:
```bash
ENVIRONMENT=development
LOG_LEVEL=DEBUG
```

### **Common Debug Scenarios**
1. **Database Issues**: Check connection strings and permissions
2. **AI Processing**: Verify OpenAI API key and credits
3. **File Processing**: Check file formats and permissions
4. **UI Issues**: Verify tkinter installation and display settings

## 📦 **Building and Distribution**

### **Create Distribution Package**
```bash
# Build package
python setup.py sdist bdist_wheel

# Install in development mode
pip install -e .
```

### **Create Executable**
```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile --windowed main.py
```

## 🔄 **Continuous Integration**

### **GitHub Actions**
The project includes GitHub Actions for:
- Automated testing
- Code quality checks
- Security scanning
- Automated releases

### **Local CI Checks**
Run CI checks locally:
```bash
# Run all checks
python scripts/ci/run_checks.py

# Individual checks
python scripts/ci/check_code_style.py
python scripts/ci/run_tests.py
python scripts/ci/security_scan.py
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Import Errors**
```bash
# Ensure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Check Python path
python -c "import sys; print(sys.path)"

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### **Database Connection Issues**
- Verify MongoDB connection string
- Check network connectivity
- Ensure database exists and is accessible

#### **OpenAI API Issues**
- Verify API key is correct
- Check API usage limits
- Ensure internet connectivity

#### **Test Failures**
- Check test database is accessible
- Verify test data is properly set up
- Run tests with verbose output for more details

### **Getting Help**
- Check the [API Documentation](api/README.md)
- Review [Project Structure](project_structure.md)
- Create an issue in the repository
- Include error logs and reproduction steps

## 📚 **Additional Resources**

- [Python Documentation](https://docs.python.org/)
- [Tkinter Tutorial](https://docs.python.org/3/library/tkinter.html)
- [MongoDB Python Driver](https://pymongo.readthedocs.io/)
- [OpenAI Python Library](https://github.com/openai/openai-python)
- [Pytest Documentation](https://docs.pytest.org/)

---

**Happy coding!** 🚀 If you have questions or need help, don't hesitate to create an issue in the repository.

