# 📚 MoneyFlowV2 Documentation

Welcome to the comprehensive documentation for MoneyFlowV2, a powerful desktop application for ingesting Excel files with intelligent schema recognition and MongoDB storage.

## 🎯 **What is MoneyFlowV2?**

MoneyFlowV2 is a professional desktop application that:
- **Ingests Excel files** with smart schema recognition
- **Uses AI-powered processing** (OpenAI GPT-4.1-nano) for column normalization
- **Stores data in MongoDB** with optimized indexing and duplicate detection
- **Manages schemas locally** using SQLite for metadata and UI state
- **Follows Windows best practices** for data storage and user privacy

## 📁 **Documentation Structure**

### **User Documentation**
- **[User Guide](user_guide/README.md)** - Complete user manual with step-by-step instructions
- **[Quick Start](user_guide/quick_start.md)** - Get up and running in 5 minutes
- **[Troubleshooting](user_guide/troubleshooting.md)** - Common issues and solutions

### **Developer Documentation**
- **[Project Structure](developer/project_structure.md)** - Architecture and code organization
- **[API Reference](api/README.md)** - Core module APIs and interfaces
- **[Development Setup](developer/setup.md)** - Environment setup and development workflow
- **[Testing Guide](testing/README.md)** - Comprehensive testing documentation

### **Deployment & Operations**
- **[Installation Guide](deployment/installation.md)** - Production deployment instructions
- **[Configuration](deployment/configuration.md)** - Environment and application settings
- **[Monitoring & Logging](deployment/monitoring.md)** - Logs, metrics, and health checks

## 🚀 **Quick Start**

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Up Environment**
   ```bash
   cp env.example .env
   # Edit .env with your OpenAI API key and MongoDB connection string
   ```

3. **Run the Application**
   ```bash
   python main.py
   ```

## 🏗️ **Architecture Overview**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Modern UI     │    │  Core Engine    │    │   Databases     │
│   (Tkinter)     │◄──►│  (Python)       │◄──►│   (SQLite +     │
│                 │    │                 │    │    MongoDB)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  File Upload    │    │ AI Processing   │    │ Data Storage    │
│  & Validation   │    │ (OpenAI API)    │    │ & Indexing      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 **Key Features**

- **Smart Schema Recognition** - AI-powered column mapping and normalization
- **Duplicate Detection** - Configurable strategies (skip, update, upsert)
- **Batch Processing** - Efficient handling of large Excel files
- **Progress Tracking** - Real-time import progress with detailed statistics
- **Error Handling** - Comprehensive error reporting and recovery
- **Audit Logging** - Complete tracking of all operations
- **Data Validation** - Input sanitization and data quality checks

## 🧪 **Testing**

The project includes comprehensive testing:

```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/integration/    # Integration tests
python -m pytest tests/e2e/           # End-to-end tests
python -m pytest tests/unit/           # Unit tests

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

## 📊 **Project Status**

- **Core Functionality**: ✅ 100% Complete
- **UI Framework**: ✅ 100% Complete  
- **AI Integration**: ✅ 100% Complete
- **Database Operations**: ✅ 100% Complete
- **Testing Suite**: ✅ 100% Complete
- **Documentation**: ✅ 100% Complete
- **Production Ready**: ✅ 100% Complete

**Overall Project Progress: 100% Complete** 🎉🎉🎉

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📞 **Support**

- **Documentation Issues**: Create an issue in the repository
- **Feature Requests**: Use the issue tracker with the "enhancement" label
- **Bug Reports**: Include detailed error logs and reproduction steps

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**MoneyFlowV2** - Professional Excel data ingestion with AI-powered intelligence 🚀

