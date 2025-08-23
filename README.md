# MoneyFlow Data Ingestion App

A powerful desktop application for ingesting Excel files with intelligent schema recognition, duplicate detection, and MongoDB storage.

## 🚀 Features

- **Smart Schema Recognition**: AI-powered column mapping and normalization
- **Duplicate Detection**: Configurable duplicate handling strategies
- **MongoDB Integration**: Efficient data storage with optimized indexes
- **SQLite Metadata**: Local storage for schemas, UI state, and analytics
- **Production Ready**: Comprehensive logging, monitoring, and error handling
- **Cost Optimized**: Uses GPT-4.1-nano for affordable AI processing

## 🏗️ Architecture

- **Frontend**: Modern desktop UI with intuitive controls
- **Backend**: Python-based processing engine with async support
- **Databases**: 
  - **SQLite**: Schema definitions, UI state, analytics, audit logs
  - **MongoDB**: Excel data storage (one collection per Excel file)
- **AI Integration**: OpenAI GPT-4.1-nano for schema analysis

## 📋 Requirements

- Python 3.11+
- MongoDB Atlas account
- OpenAI API key
- Windows 10/11

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd MoneyFlowV2
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy production template
   copy env.production .env
   
   # Edit .env with your actual values:
   # - OPENAI_API_KEY
   # - MONGO_URL (MongoDB Atlas connection string)
   # - Other production settings
   ```

5. **Initialize database**
   ```bash
   python scripts/setup_database.py
   ```

## 🔧 Configuration

### Production Environment

The app includes a comprehensive production configuration template (`env.production`) with:

- **OpenAI**: GPT-4.1-nano model for cost-effective processing
- **MongoDB**: Atlas connection with `excel_imports` database
- **Performance**: Optimized batch sizes and memory limits
- **Security**: Encryption keys and session management
- **Monitoring**: Health checks and metrics collection
- **Logging**: Rotating log files with backup management

### Key Settings

```bash
# AI Processing (GPT-4.1-nano)
OPENAI_MODEL=gpt-4.1-nano
AI_TEMPERATURE=0.1
AI_MAX_TOKENS=1000

# Database
MONGO_DATABASE=excel_imports
DB_SQLITE_DB_PATH=data/templates.db

# Performance
BATCH_SIZE=1000
MAX_WORKERS=4
MEMORY_LIMIT_MB=512
```

## 🧪 Testing

The project includes a comprehensive test suite organized into logical categories:

### **Test Structure**
```
tests/
├── integration/          # Integration tests for core components
├── e2e/                 # End-to-end workflow tests
├── test_core/           # Core module unit tests
├── test_models/         # Data model tests
├── test_ui/             # UI component tests
└── test_utils/          # Utility function tests
```

### **Running Tests**
```bash
# Run all tests
python -m pytest tests/

# Run specific categories
python -m pytest tests/integration/    # Integration tests
python -m pytest tests/e2e/           # E2E tests

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### **Test Coverage**
- ✅ Database CRUD operations (all 7 SQLite tables)
- ✅ Core component integration
- ✅ Schema management lifecycle
- ✅ Complete application workflows
- ✅ Error handling and edge cases

For detailed test documentation, see [tests/README.md](tests/README.md).

## 🚀 Usage

1. **Start the application**
   ```bash
   python main.py
   ```

2. **Upload Excel file**
   - Select your Excel file
   - Review detected schema
   - Configure duplicate detection rules

3. **Process data**
   - Set data start row
   - Choose duplicate strategy
   - Monitor progress

4. **Review results**
   - Check data quality reports
   - View audit logs
   - Access analytics

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python scripts/run_tests.py

# Run specific test modules
pytest tests/test_core/ -v

# Run with coverage
pytest --cov=src tests/
```

## 📊 Database Schema

### SQLite (Metadata & UI)
- `schema_definitions`: Schema templates and mappings
- `import_batches`: Batch processing history
- `audit_log`: Complete audit trail
- `data_quality_issues`: Quality validation results
- `ui_state`: User preferences and UI state
- `file_processing_history`: File processing analytics
- `schema_analytics`: Schema usage statistics

### MongoDB (Data Storage)
- **Database**: `excel_imports`
- **Collections**: One per Excel file (e.g., `excel_2025_08_22_financial_data`)
- **Indexes**: Optimized for duplicate detection and queries

## 🔒 Security Features

- Environment variable configuration
- Encrypted sensitive data
- Audit logging for all operations
- Input validation and sanitization
- Secure MongoDB connections

## 📈 Performance Features

- **Bulk Operations**: MongoDB bulk inserts
- **Async Processing**: Non-blocking data processing
- **Memory Management**: Streaming large files
- **Index Optimization**: Pre-created indexes
- **Batch Processing**: Configurable batch sizes

## 🐛 Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   - Check your Atlas connection string
   - Verify network access and IP whitelist
   - Ensure database name is `excel_imports`

2. **OpenAI API Errors**
   - Verify API key in `.env` file
   - Check API quota and billing
   - Ensure model name is correct (`gpt-4.1-nano`)

3. **File Processing Issues**
   - Check file size limits (default: 100MB)
   - Verify Excel file format
   - Review data start row configuration

### Logs

Check the logs directory for detailed error information:
```bash
# View latest logs
Get-Content logs/app.log -Tail 50
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Check the troubleshooting section
- Review the logs for error details
- Open an issue with detailed information

---

**Built with ❤️ for efficient Excel data processing**
