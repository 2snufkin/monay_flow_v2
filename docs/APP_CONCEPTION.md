# MoneyFlow Data Ingestion App - Complete Conception Document

## 🎯 Project Overview

**MoneyFlow** is a desktop application designed to intelligently process Excel files and store them in MongoDB with AI-powered schema normalization. The app remembers user-defined duplicate detection logic and collection metadata (templates) so that future uploads with the same structure can automatically apply the same rules.

## 🏗️ Architecture Overview

### Hybrid Database Design
- **SQLite**: Local storage for metadata, UI state, schema definitions, import history, audit logs, data quality issues, schema analytics
- **MongoDB**: Cloud storage for actual Excel data, single database (`excel_imports`), collections per Excel file (e.g., `excel_file_001`)

### Core Components
1. **SchemaManager**: Manages schema definitions and templates
2. **AIProcessor**: OpenAI integration for column normalization
3. **ExcelProcessor**: Excel file reading and validation
4. **MongoCollectionManager**: MongoDB operations and indexing
5. **DataIngestionEngine**: Orchestrates the entire pipeline
6. **UI Controllers**: Desktop interface management

## 🎨 UI/UX Design & Flow

### Initial Launch Behavior
When the app launches:
1. **Query SQL database** for predefined schema fingerprints
2. **Populate dropdown** with existing schema names
3. **If empty**: Show modal prompting for new schema definition

### Main Application Window

#### Header Section
```
┌─────────────────────────────────────────────────────────────────┐
│ 🚀 MoneyFlow Data Ingestion App                    [Settings] │
├─────────────────────────────────────────────────────────────────┤
│ Current Schema: [Dropdown: Select Schema ▼] [Create New +]    │
└─────────────────────────────────────────────────────────────────┘
```

#### File Selection & Configuration
```
┌─────────────────────────────────────────────────────────────────┐
│ 📁 Excel File Selection                                        │
│ [Browse Files] [Drag & Drop Area]                              │
│ Selected: test_data.xlsx                                       │
│                                                                 │
│ ⚙️ Processing Configuration                                    │
│ Data Start Row: [Dropdown: 1-10] (Default: 2)                 │
│ Duplicate Strategy: [Dropdown: Skip/Update/Upsert] (Default: Skip) │
│                                                                 │
│ [Preview Data] [Start Import]                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Data Preview Panel
```
┌─────────────────────────────────────────────────────────────────┐
│ 👀 Data Preview (First 5 rows)                                │
├─────────────────────────────────────────────────────────────────┤
│ Purchase Date │ Item Name │ Category │ Amount │ Payment Method │
├─────────────────────────────────────────────────────────────────┤
│ 2025-08-21   │ Product 2 │ Electronics│ 466.25│ PayPal        │
│ 2025-08-20   │ Product 3 │ Electronics│ 138.41│ PayPal        │
│ 2025-08-19   │ Product 4 │ Electronics│ 231.43│ Credit Card   │
│ ...           │ ...       │ ...       │ ...   │ ...            │
└─────────────────────────────────────────────────────────────────┘
```

#### Progress & Status
```
┌─────────────────────────────────────────────────────────────────┐
│ 📊 Import Progress                                             │
│ [████████████████████████████████████████████████████████████] │
│ Processing row 45 of 100...                                    │
│ ✅ 45 documents inserted | ⚠️ 0 duplicates skipped             │
│                                                                 │
│ [Pause] [Stop] [View Results]                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Schema Creation Modal

#### New Schema Definition Flow
```
┌─────────────────────────────────────────────────────────────────┐
│ 🆕 Create New Schema                                           │
├─────────────────────────────────────────────────────────────────┤
│ Schema Name: [________________________]                        │
│                                                                 │
│ 📋 Paste Excel Column Names (one per line):                   │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Purchase Date                                              │ │
│ │ Item Name                                                  │ │
│ │ Category                                                   │ │
│ │ Amount                                                     │ │
│ │ Payment Method                                             │ │
│ │ Store                                                      │ │
│ │ Customer ID                                                │ │
│ │ Email                                                      │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ [Process with AI] [Create Manually]                            │
└─────────────────────────────────────────────────────────────────┘
```

#### AI Processing Results
```
┌─────────────────────────────────────────────────────────────────┐
│ 🤖 AI Schema Processing Results                                │
├─────────────────────────────────────────────────────────────────┤
│ ✅ Column Normalization:                                       │
│   "Purchase Date" → "purchase_date" (datetime)                 │
│   "Item Name" → "item_name" (string)                          │
│   "Amount" → "amount" (decimal)                                │
│                                                                 │
│ 📑 Suggested Indexes:                                          │
│   • purchase_date (ascending)                                  │
│   • customer_id (unique)                                       │
│   • amount (descending)                                        │
│                                                                 │
│ 🔍 Duplicate Detection Columns:                                │
│   • customer_id + email                                        │
│   • purchase_date + item_name + amount                         │
│                                                                 │
│ [Accept & Create] [Modify] [Cancel]                            │
└─────────────────────────────────────────────────────────────────┘
```

### Schema Management Dashboard

#### Template Library
```
┌─────────────────────────────────────────────────────────────────┐
│ 📚 Schema Templates                                            │
├─────────────────────────────────────────────────────────────────┤
│ 🔍 Search: [________________________] [Filter ▼]              │
│                                                                 │
│ ┌─────────────┬─────────────┬─────────────┬─────────────┬─────┐ │
│ │ Schema Name│ Last Used   │ Usage Count │ Columns     │ ... │ │
│ ├─────────────┼─────────────┼─────────────┼─────────────┼─────┤ │
│ │ Sales Data │ 2025-08-22  │ 15          │ 8           │ [Edit] │
│ │ Inventory  │ 2025-08-20  │ 8           │ 12          │ [Edit] │
│ │ Expenses   │ 2025-08-18  │ 23          │ 6           │ [Edit] │
│ └─────────────┴─────────────┴─────────────┴─────────────┴─────┘ │
│                                                                 │
│ [Create New] [Import Schema] [Export Schema]                   │
└─────────────────────────────────────────────────────────────────┘
```

#### Schema Editor
```
┌─────────────────────────────────────────────────────────────────┐
│ ✏️ Edit Schema: Sales Data                                     │
├─────────────────────────────────────────────────────────────────┤
│ Schema Name: [Sales Data________________]                      │
│                                                                 │
│ 📋 Column Mappings:                                            │
│ ┌─────────────────┬─────────────────┬─────────────────────────┐ │
│ │ Excel Column    │ MongoDB Field   │ Data Type               │ │
│ ├─────────────────┼─────────────────┼─────────────────────────┤ │
│ │ Purchase Date   │ purchase_date   │ [datetime ▼]            │
│ │ Item Name       │ item_name       │ [string ▼]              │
│ │ Category        │ category        │ [string ▼]              │
│ │ Amount          │ amount          │ [decimal ▼]              │
│ └─────────────────┴─────────────────┴─────────────────────────┘ │
│                                                                 │
│ 🔍 Duplicate Detection:                                        │
│ [x] customer_id + email                                        │
│ [x] purchase_date + item_name + amount                         │
│ [ ] amount > 1000                                              │
│                                                                 │
│ [Save Changes] [Test Schema] [Delete Schema]                   │
└─────────────────────────────────────────────────────────────────┘
```

### Import History & Rollback

#### Batch History
```
┌─────────────────────────────────────────────────────────────────┐
│ 📊 Import History                                              │
├─────────────────────────────────────────────────────────────────┤
│ 🔍 Filter: [Date Range ▼] [Schema ▼] [Status ▼]               │
│                                                                 │
│ ┌─────────────┬─────────────┬─────────────┬─────────────┬─────┐ │
│ │ Date       │ File Name   │ Schema      │ Rows        │ ... │ │
│ ├─────────────┼─────────────┼─────────────┼─────────────┼─────┤ │
│ │ 2025-08-22 │ sales.xlsx  │ Sales Data  │ 150         │ [View] │
│ │ 2025-08-21 │ inventory.xl│ Inventory   │ 89          │ [View] │
│ │ 2025-08-20 │ expenses.xls│ Expenses    │ 67          │ [View] │
│ └─────────────┴─────────────┴─────────────┴─────────────┴─────┘ │
│                                                                 │
│ [Rollback Batch] [Export Results] [View Details]               │
└─────────────────────────────────────────────────────────────────┘
```

#### Rollback Confirmation
```
┌─────────────────────────────────────────────────────────────────┐
│ ⚠️ Rollback Confirmation                                       │
├─────────────────────────────────────────────────────────────────┤
│ Are you sure you want to rollback this import?                │
│                                                                 │
│ 📋 Batch Details:                                              │
│ • File: sales.xlsx                                             │
│ • Schema: Sales Data                                           │
│ • Rows: 150                                                    │
│ • Date: 2025-08-22 14:30:15                                   │
│                                                                 │
│ ⚠️ This action will:                                           │
│ • Remove all 150 documents from MongoDB                        │
│ • Update audit logs                                            │
│ • Cannot be undone                                             │
│                                                                 │
│ [Confirm Rollback] [Cancel]                                    │
└─────────────────────────────────────────────────────────────────┘
```

### Data Quality Reports

#### Quality Dashboard
```
┌─────────────────────────────────────────────────────────────────┐
│ 📈 Data Quality Dashboard                                      │
├─────────────────────────────────────────────────────────────────┤
│ 📊 Overall Quality Score: 94%                                 │
│                                                                 │
│ ┌─────────────────┬─────────────┬─────────────┬─────────────┐ │
│ │ Metric          │ Current     │ Previous    │ Trend       │ │
│ ├─────────────────┼─────────────┼─────────────┼─────────────┤ │
│ │ Completeness    │ 98%         │ 95%         │ ↗️ +3%      │ │
│ │ Accuracy        │ 92%         │ 89%         │ ↗️ +3%      │ │
│ │ Consistency     │ 96%         │ 94%         │ ↗️ +2%      │ │
│ │ Timeliness      │ 100%        │ 100%        │ → 0%        │ │
│ └─────────────────┴─────────────┴─────────────┴─────────────┘ │
│                                                                 │
│ 🚨 Issues Found:                                               │
│ • 3 missing email addresses                                   │
│ • 2 duplicate customer IDs                                     │
│ • 1 invalid amount format                                      │
│                                                                 │
│ [View Details] [Export Report] [Fix Issues]                    │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow & Processing

### 1. Excel File Upload
```
User selects Excel file → File validation → Column extraction → Schema matching
```

### 2. Schema Processing
```
If new schema: AI processing → Column normalization → Index suggestions → Save template
If existing schema: Load template → Apply settings → Validate compatibility
```

### 3. Data Ingestion
```
Read Excel rows → Transform data → Check duplicates → Insert into MongoDB → Update audit logs
```

### 4. Quality Assurance
```
Data validation → Quality scoring → Issue reporting → Rollback capability
```

## 🚀 Key Features

### Smart Schema Memory & Reuse
- **Schema Fingerprinting**: Generate unique identifiers for Excel structures
- **Auto-Matching Logic**: Automatically detect and apply saved schemas
- **Template Management**: Save, edit, and version control schemas

### AI-Powered Processing
- **Column Normalization**: Convert Excel names to MongoDB field names
- **Data Type Inference**: Automatically detect appropriate data types
- **Index Optimization**: Suggest optimal MongoDB indexes
- **Duplicate Detection**: Recommend columns for duplicate checking

### Performance & Reliability
- **Bulk Operations**: MongoDB bulk inserts for efficiency
- **Streaming Processing**: Handle large files without memory issues
- **Async Processing**: Non-blocking UI during data import
- **Rollback Capability**: Undo imports using audit logs

### Data Quality & Monitoring
- **Real-time Validation**: Check data during import
- **Quality Scoring**: Track data quality metrics over time
- **Issue Reporting**: Identify and report data problems
- **Audit Logging**: Complete trail of all operations

## 🎯 User Experience Goals

### Simplicity
- **One-Click Import**: Upload Excel, select schema, click import
- **Smart Defaults**: Sensible defaults for common scenarios
- **Progressive Disclosure**: Show advanced options only when needed

### Automation
- **Auto-Schema Detection**: Recognize file structures automatically
- **Template Reuse**: Apply previous settings without reconfiguration
- **Batch Processing**: Handle multiple files efficiently

### Flexibility
- **Schema Override**: Customize any saved template
- **Custom Rules**: Define business-specific validation rules
- **Export Options**: Multiple output formats and destinations

## 🔧 Technical Implementation

### Frontend Framework
- **Tkinter**: Native Python GUI framework for cross-platform compatibility
- **Custom Widgets**: Specialized components for data processing workflows
- **Responsive Design**: Adapt to different screen sizes and resolutions

### Backend Architecture
- **Modular Design**: Separate concerns for maintainability
- **Async Processing**: Non-blocking operations for better UX
- **Error Handling**: Comprehensive error management and user feedback
- **Logging**: Detailed logging for debugging and monitoring

### Database Design
- **SQLite**: Fast local storage for metadata and UI state
- **MongoDB**: Scalable cloud storage for Excel data
- **Connection Pooling**: Efficient database connections
- **Indexing Strategy**: Optimized for query performance

## 📋 Development Roadmap

### Phase 1: Core UI (Current)
- [x] Backend architecture and components
- [x] Database setup and configuration
- [ ] Main application window
- [ ] File selection and preview
- [ ] Basic schema management

### Phase 2: AI Integration
- [ ] OpenAI API integration
- [ ] Column normalization
- [ ] Schema suggestions
- [ ] Duplicate detection logic

### Phase 3: Advanced Features
- [ ] Data quality monitoring
- [ ] Rollback capabilities
- [ ] Batch processing
- [ ] Performance optimization

### Phase 4: Production Ready
- [ ] Error handling and recovery
- [ ] User preferences and settings
- [ ] Documentation and help
- [ ] Testing and validation

## 🎨 UI Design Principles

### Visual Hierarchy
- **Clear Information Architecture**: Logical grouping of related functions
- **Progressive Disclosure**: Show complexity only when needed
- **Consistent Layout**: Standardized positioning and spacing

### User Feedback
- **Real-time Updates**: Show progress and status immediately
- **Clear Messaging**: Informative error messages and confirmations
- **Visual Indicators**: Icons, colors, and animations for status

### Accessibility
- **Keyboard Navigation**: Full keyboard support for power users
- **Screen Reader Support**: Proper labeling and descriptions
- **High Contrast**: Readable text and interface elements

This conception document outlines the complete vision for the MoneyFlow Data Ingestion App, combining powerful backend processing with an intuitive and efficient user interface that makes Excel data management simple and automated.

