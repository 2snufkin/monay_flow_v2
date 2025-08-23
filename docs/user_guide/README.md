# 👤 MoneyFlowV2 User Guide

Welcome to the MoneyFlowV2 user guide! This guide will walk you through using the application to ingest Excel files with intelligent schema recognition.

## 📋 **Table of Contents**

1. [Getting Started](#getting-started)
2. [First Time Setup](#first-time-setup)
3. [Creating Your First Schema](#creating-your-first-schema)
4. [Importing Excel Files](#importing-excel-files)
5. [Managing Schemas](#managing-schemas)
6. [Troubleshooting](#troubleshooting)

## 🚀 **Getting Started**

### **What You Need**
- **OpenAI API Key** - For AI-powered schema recognition
- **MongoDB Atlas Account** - For data storage (free tier available)
- **Excel Files** - The data you want to import

### **System Requirements**
- Windows 10/11
- Python 3.11+ (included with the application)
- Internet connection for AI processing and MongoDB

## ⚙️ **First Time Setup**

### **1. Launch the Application**
```bash
python main.py
```

### **2. Configure Settings**
- Click the **Settings** button (gear icon)
- Enter your **OpenAI API Key**
- Enter your **MongoDB Connection String**
- Click **Save**

### **3. Verify Connection**
- The application will test your connections
- Green checkmarks indicate successful connections
- Red X marks indicate connection issues

## 🏗️ **Creating Your First Schema**

### **What is a Schema?**
A schema defines how your Excel data should be processed:
- **Column Mapping** - How Excel columns map to database fields
- **Data Types** - What type of data each column contains
- **Duplicate Detection** - How to handle duplicate records
- **Indexing** - How to optimize database queries

### **Step 1: Define Schema**
1. Click **"Define Schema"** button
2. Enter a descriptive **Schema Name** (e.g., "Customer Data")
3. **Paste your Excel column headers** into the text area
4. Click **"Process with AI"**

### **Step 2: Review AI Suggestions**
The AI will analyze your columns and suggest:
- **Normalized field names** (e.g., "First Name" → "first_name")
- **Data types** (String, Number, Date, etc.)
- **Indexes** for performance optimization
- **Duplicate detection columns**

### **Step 3: Customize (Optional)**
- Modify field names if needed
- Adjust data types
- Select which columns to use for duplicate detection
- Choose duplicate strategy (skip, update, or upsert)

### **Step 4: Save Schema**
- Click **"Save Schema"**
- Your schema is now available for future imports

## 📊 **Importing Excel Files**

### **Step 1: Select File**
1. Click **"Browse Files"**
2. Navigate to your Excel file
3. Select the file and click **"Open"**

### **Step 2: Choose Schema**
- Select your saved schema from the dropdown
- The application will automatically detect if your file matches an existing schema
- If no match is found, you can create a new schema

### **Step 3: Configure Import**
- **Data Start Row**: Specify which row contains actual data (default: 2)
- **Duplicate Strategy**: Choose how to handle duplicates
- **Batch Size**: Number of records to process at once (default: 1000)

### **Step 4: Preview Data**
- Click **"Preview Data"** to see the first few rows
- Verify column mapping is correct
- Check data types and formatting

### **Step 5: Start Import**
- Click **"Import Data"**
- Monitor progress in the progress bar
- View real-time statistics:
  - Total rows processed
  - Records inserted
  - Duplicates skipped
  - Errors encountered

## 🔧 **Managing Schemas**

### **View All Schemas**
- Schemas are listed in the main dropdown
- Each schema shows:
  - Name and description
  - Number of columns
  - Last used date
  - Usage count

### **Edit Schema**
1. Select the schema from dropdown
2. Click **"Edit Schema"**
3. Modify settings as needed
4. Click **"Save Changes"**

### **Delete Schema**
1. Select the schema from dropdown
2. Click **"Delete Schema"**
3. Confirm deletion
4. **Note**: This only removes the schema definition, not the imported data

## 📈 **Monitoring and Reports**

### **Import History**
- View all previous imports
- See success/failure rates
- Check processing times
- Review error logs

### **Data Quality Reports**
- Column completeness analysis
- Data type validation results
- Duplicate detection statistics
- Performance metrics

## 🚨 **Troubleshooting**

### **Common Issues**

#### **"OpenAI API Error"**
- Check your API key is correct
- Verify you have sufficient API credits
- Check internet connection

#### **"MongoDB Connection Failed"**
- Verify connection string format
- Check network connectivity
- Ensure MongoDB Atlas is accessible

#### **"Schema Not Found"**
- Create a new schema for your file structure
- Check column names match exactly
- Verify data start row is correct

#### **"Import Failed"**
- Check Excel file format (.xlsx, .xls)
- Verify file isn't corrupted
- Check file size isn't too large
- Review error logs for specific issues

### **Getting Help**
- Check the [Troubleshooting Guide](troubleshooting.md)
- Review application logs
- Create an issue in the repository
- Include error messages and file samples

## 💡 **Best Practices**

### **Schema Design**
- Use descriptive schema names
- Include all relevant columns
- Set appropriate duplicate detection
- Choose meaningful field names

### **Data Preparation**
- Clean your Excel data before import
- Ensure consistent column headers
- Remove empty rows and columns
- Validate data types

### **Performance**
- Use appropriate batch sizes
- Create indexes for frequently queried fields
- Monitor import performance
- Clean up old schemas if not needed

## 🔄 **Advanced Features**

### **Batch Processing**
- Import multiple files with the same schema
- Schedule automated imports
- Process files in background

### **Data Validation**
- Custom validation rules
- Data quality checks
- Error reporting and logging

### **Rollback Capability**
- Undo recent imports
- Restore previous data states
- Audit trail for all changes

---

**Need more help?** Check the [Troubleshooting Guide](troubleshooting.md) or create an issue in the repository.

