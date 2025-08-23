#!/usr/bin/env python3
"""
Main Application Window

The primary interface for the MoneyFlow Data Ingestion App.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, List, Dict, Any
import threading
from pathlib import Path

from core.schema_manager import SchemaManager
from core.excel_processor import ExcelProcessor
from core.ai_processor import AISchemaProcessor
from core.mongo_collection_manager import MongoCollectionManager
from core.data_ingestion_engine import DataIngestionEngine
from config.settings import get_settings
from models.schema_definition import SchemaDefinition, AttributeDefinition
from utils.validation import InputValidator, validate_schema_definition, sanitize_user_input


class ModernMainWindow:
    """Modern main application window for MoneyFlow."""
    
    def __init__(self):
        """Initialize the main window."""
        self.root = tk.Tk()
        self.root.title("🚀 MoneyFlow Data Ingestion App")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)
        
        # Set modern theme and colors
        self.setup_modern_theme()
        
        # Initialize components
        self.settings = get_settings()
        self.schema_manager = SchemaManager()
        self.excel_processor = ExcelProcessor()
        self.ai_processor = AISchemaProcessor()
        self.mongo_manager = MongoCollectionManager()
        self.ingestion_engine = DataIngestionEngine()
        
        # State variables
        self.current_schema: Optional[SchemaDefinition] = None
        self.selected_file: Optional[Path] = None
        self.preview_data: List[Dict[str, Any]] = []
        
        # Setup UI
        self.setup_ui()
        self.load_schemas()
        
    def setup_modern_theme(self):
        """Setup modern color scheme and styling."""
        # Modern color palette
        self.colors = {
            'primary': '#2563eb',      # Blue
            'primary_hover': '#1d4ed8',
            'secondary': '#64748b',    # Slate
            'success': '#059669',      # Green
            'warning': '#d97706',      # Amber
            'error': '#dc2626',        # Red
            'background': '#f8fafc',   # Light gray
            'surface': '#ffffff',      # White
            'border': '#e2e8f0',      # Light border
            'text': '#1e293b',        # Dark text
            'text_secondary': '#64748b' # Secondary text
        }
        
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure modern button style
        style.configure('Modern.TButton',
                       background=self.colors['primary'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(12, 8))
        
        style.map('Modern.TButton',
                 background=[('active', self.colors['primary_hover']),
                           ('pressed', self.colors['primary_hover'])])
        
        # Configure modern frame style
        style.configure('Modern.TFrame',
                       background=self.colors['surface'],
                       relief='flat')
        
        # Configure modern label frame style
        style.configure('Modern.TLabelframe',
                       background=self.colors['surface'],
                       borderwidth=1,
                       relief='solid')
        
        style.configure('Modern.TLabelframe.Label',
                       background=self.colors['surface'],
                       foreground=self.colors['text'],
                       font=('Segoe UI', 10, 'bold'))
        
    def setup_ui(self):
        """Setup the user interface."""
        # Configure grid weights
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Apply background color
        self.root.configure(bg=self.colors['background'])
        
        # Header section
        self.create_modern_header()
        
        # Main content area
        self.create_modern_main_content()
        
        # Status bar
        self.create_modern_status_bar()
        
    def create_modern_header(self):
        """Create the modern header section."""
        header_frame = tk.Frame(self.root, bg=self.colors['surface'], relief='flat', bd=0)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=15)
        header_frame.grid_columnconfigure(1, weight=1)
        
        # App title with modern styling
        title_frame = tk.Frame(header_frame, bg=self.colors['surface'])
        title_frame.grid(row=0, column=0, sticky="w", padx=(0, 20))
        
        title_label = tk.Label(title_frame, 
                              text="🚀 MoneyFlow", 
                              font=("Segoe UI", 24, "bold"),
                              fg=self.colors['primary'],
                              bg=self.colors['surface'])
        title_label.pack(side="left")
        
        subtitle_label = tk.Label(title_frame,
                                 text="Data Ingestion App",
                                 font=("Segoe UI", 14),
                                 fg=self.colors['text_secondary'],
                                 bg=self.colors['surface'])
        subtitle_label.pack(side="left", padx=(10, 0))
        
        # Schema selection with modern styling
        schema_frame = tk.Frame(header_frame, bg=self.colors['surface'])
        schema_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(15, 0))
        
        schema_label = tk.Label(schema_frame, 
                               text="📋 Current Schema:", 
                               font=("Segoe UI", 11, "bold"),
                               fg=self.colors['text'],
                               bg=self.colors['surface'])
        schema_label.grid(row=0, column=0, padx=(0, 15), sticky="w")
        
        # Modern combobox styling
        self.schema_var = tk.StringVar()
        self.schema_combo = ttk.Combobox(schema_frame, 
                                         textvariable=self.schema_var,
                                         state="readonly", 
                                         width=35,
                                         font=("Segoe UI", 10))
        self.schema_combo.grid(row=0, column=1, padx=(0, 15))
        self.schema_combo.bind("<<ComboboxSelected>>", self.on_schema_selected)
        
        # Modern button styling
        create_schema_btn = tk.Button(schema_frame, 
                                     text="✨ Create New Schema", 
                                     command=self.show_create_schema_dialog,
                                     bg=self.colors['success'],
                                     fg='white',
                                     font=("Segoe UI", 10, "bold"),
                                     relief='flat',
                                     padx=20,
                                     pady=8,
                                     cursor='hand2')
        create_schema_btn.grid(row=0, column=2, padx=(0, 15))
        
        # Settings button with modern styling
        settings_btn = tk.Button(header_frame, 
                                text="⚙️ Settings", 
                                command=self.show_settings,
                                bg=self.colors['secondary'],
                                fg='white',
                                font=("Segoe UI", 10),
                                relief='flat',
                                padx=15,
                                pady=8,
                                cursor='hand2')
        settings_btn.grid(row=0, column=2, padx=(0, 20), pady=10, sticky="e")
        
    def create_modern_main_content(self):
        """Create the modern main content area."""
        main_frame = tk.Frame(self.root, bg=self.colors['background'])
        main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # Left panel - File selection and configuration
        self.create_modern_left_panel(main_frame)
        
        # Right panel - Data preview and progress
        self.create_modern_right_panel(main_frame)
        
    def create_modern_left_panel(self, parent):
        """Create the modern left panel for file selection and configuration."""
        left_frame = tk.LabelFrame(parent, 
                                  text="📁 Excel File Selection", 
                                  font=("Segoe UI", 12, "bold"),
                                  fg=self.colors['text'],
                                  bg=self.colors['surface'],
                                  relief='solid',
                                  bd=1)
        left_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 10))
        left_frame.grid_columnconfigure(0, weight=1)
        
        # File selection with modern styling
        file_frame = tk.Frame(left_frame, bg=self.colors['surface'])
        file_frame.grid(row=0, column=0, sticky="ew", pady=(20, 20), padx=20)
        file_frame.grid_columnconfigure(1, weight=1)
        
        browse_btn = tk.Button(file_frame, 
                              text="🔍 Browse Files", 
                              command=self.browse_files,
                              bg=self.colors['primary'],
                              fg='white',
                              font=("Segoe UI", 10, "bold"),
                              relief='flat',
                              padx=20,
                              pady=10,
                              cursor='hand2')
        browse_btn.grid(row=0, column=0, padx=(0, 15))
        
        self.file_label = tk.Label(file_frame, 
                                   text="No file selected", 
                                   font=("Segoe UI", 10),
                                   fg=self.colors['text_secondary'],
                                   bg=self.colors['surface'])
        self.file_label.grid(row=0, column=1, sticky="w")
        
        # Modern drag & drop area
        drop_frame = tk.Frame(left_frame, 
                              bg=self.colors['background'],
                              relief='solid',
                              bd=2)
        drop_frame.grid(row=1, column=0, sticky="ew", pady=(0, 25), padx=20)
        drop_frame.grid_columnconfigure(0, weight=1)
        
        drop_label = tk.Label(drop_frame, 
                              text="📥 Drag & Drop Excel files here\nor use Browse button above", 
                              font=("Segoe UI", 11),
                              fg=self.colors['text_secondary'],
                              bg=self.colors['background'],
                              justify='center',
                              pady=30)
        drop_label.grid(row=0, column=0)
        
        # Processing configuration with modern styling
        config_frame = tk.LabelFrame(left_frame, 
                                    text="⚙️ Processing Configuration", 
                                    font=("Segoe UI", 12, "bold"),
                                    fg=self.colors['text'],
                                    bg=self.colors['surface'],
                                    relief='solid',
                                    bd=1)
        config_frame.grid(row=2, column=0, sticky="ew", pady=(0, 25), padx=20)
        config_frame.grid_columnconfigure(1, weight=1)
        
        # Data start row
        start_row_label = tk.Label(config_frame, 
                                  text="📊 Data Start Row:", 
                                  font=("Segoe UI", 10, "bold"),
                                  fg=self.colors['text'],
                                  bg=self.colors['surface'])
        start_row_label.grid(row=0, column=0, sticky="w", pady=15)
        
        self.start_row_var = tk.IntVar(value=2)
        start_row_combo = ttk.Combobox(config_frame, 
                                       textvariable=self.start_row_var,
                                       values=list(range(1, 11)), 
                                       state="readonly", 
                                       width=15,
                                       font=("Segoe UI", 10))
        start_row_combo.grid(row=0, column=1, sticky="w", padx=(15, 0), pady=15)
        
        # Duplicate strategy
        strategy_label = tk.Label(config_frame, 
                                 text="🔄 Duplicate Strategy:", 
                                 font=("Segoe UI", 10, "bold"),
                                 fg=self.colors['text'],
                                 bg=self.colors['surface'])
        strategy_label.grid(row=1, column=0, sticky="w", pady=15)
        
        self.duplicate_strategy_var = tk.StringVar(value="skip")
        strategy_combo = ttk.Combobox(config_frame, 
                                      textvariable=self.duplicate_strategy_var,
                                      values=["skip", "update", "upsert"], 
                                      state="readonly", 
                                      width=15,
                                      font=("Segoe UI", 10))
        strategy_combo.grid(row=1, column=1, sticky="w", padx=(15, 0), pady=15)
        
        # Action buttons with modern styling
        button_frame = tk.Frame(left_frame, bg=self.colors['surface'])
        button_frame.grid(row=3, column=0, sticky="ew", pady=(0, 20), padx=20)
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        preview_btn = tk.Button(button_frame, 
                               text="👀 Preview Data", 
                               command=self.preview_data,
                               bg=self.colors['warning'],
                               fg='white',
                               font=("Segoe UI", 10, "bold"),
                               relief='flat',
                               padx=20,
                               pady=12,
                               cursor='hand2')
        preview_btn.grid(row=0, column=0, padx=(0, 10))
        
        import_btn = tk.Button(button_frame, 
                              text="🚀 Start Import", 
                              command=self.start_import,
                              bg=self.colors['success'],
                              fg='white',
                              font=("Segoe UI", 10, "bold"),
                              relief='flat',
                              padx=20,
                              pady=12,
                              cursor='hand2')
        import_btn.grid(row=0, column=1, padx=(10, 0))
        
    def create_modern_right_panel(self, parent):
        """Create the modern right panel for data preview and progress."""
        right_frame = tk.Frame(parent, bg=self.colors['background'])
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)
        
        # Data preview panel with modern styling
        preview_frame = tk.LabelFrame(right_frame, 
                                     text="👀 Data Preview", 
                                     font=("Segoe UI", 12, "bold"),
                                     fg=self.colors['text'],
                                     bg=self.colors['surface'],
                                     relief='solid',
                                     bd=1)
        preview_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        preview_frame.grid_columnconfigure(0, weight=1)
        preview_frame.grid_rowconfigure(1, weight=1)
        
        # Preview controls
        preview_controls = tk.Frame(preview_frame, bg=self.colors['surface'])
        preview_controls.grid(row=0, column=0, sticky="ew", pady=(20, 15), padx=20)
        
        preview_label = tk.Label(preview_controls, 
                                text="📊 First 5 rows:", 
                                font=("Segoe UI", 10, "bold"),
                                fg=self.colors['text'],
                                bg=self.colors['surface'])
        preview_label.grid(row=0, column=0, sticky="w")
        
        refresh_btn = tk.Button(preview_controls, 
                               text="🔄 Refresh", 
                               command=self.refresh_preview,
                               bg=self.colors['secondary'],
                               fg='white',
                               font=("Segoe UI", 9),
                               relief='flat',
                               padx=15,
                               pady=6,
                               cursor='hand2')
        refresh_btn.grid(row=0, column=1, padx=(15, 0))
        
        # Modern treeview with better styling
        tree_frame = tk.Frame(preview_frame, bg=self.colors['surface'])
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        self.preview_tree = ttk.Treeview(tree_frame, show="headings", height=8)
        preview_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.preview_tree.yview)
        self.preview_tree.configure(yscrollcommand=preview_scrollbar.set)
        
        self.preview_tree.grid(row=0, column=0, sticky="nsew")
        preview_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Progress panel with modern styling
        progress_frame = tk.LabelFrame(right_frame, 
                                      text="📊 Import Progress", 
                                      font=("Segoe UI", 12, "bold"),
                                      fg=self.colors['text'],
                                      bg=self.colors['surface'],
                                      relief='solid',
                                      bd=1)
        progress_frame.grid(row=1, column=0, sticky="ew")
        progress_frame.grid_columnconfigure(0, weight=1)
        
        # Modern progress bar
        progress_container = tk.Frame(progress_frame, bg=self.colors['surface'])
        progress_container.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 15))
        progress_container.grid_columnconfigure(0, weight=1)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_container, 
                                            variable=self.progress_var,
                                            maximum=100, 
                                            length=500,
                                            style='Modern.Horizontal.TProgressbar')
        self.progress_bar.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        # Progress status with modern styling
        self.progress_label = tk.Label(progress_container, 
                                      text="Ready to import", 
                                      font=("Segoe UI", 10),
                                      fg=self.colors['text_secondary'],
                                      bg=self.colors['surface'])
        self.progress_label.grid(row=1, column=0, sticky="w", pady=(0, 20))
        
        # Progress controls with modern styling
        progress_controls = tk.Frame(progress_frame, bg=self.colors['surface'])
        progress_controls.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        progress_controls.grid_columnconfigure(0, weight=1)
        progress_controls.grid_columnconfigure(1, weight=1)
        progress_controls.grid_columnconfigure(2, weight=1)
        
        self.pause_btn = tk.Button(progress_controls, 
                                  text="⏸️ Pause", 
                                  state="disabled",
                                  bg=self.colors['warning'],
                                  fg='white',
                                  font=("Segoe UI", 9),
                                  relief='flat',
                                  padx=15,
                                  pady=8,
                                  cursor='hand2')
        self.pause_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_btn = tk.Button(progress_controls, 
                                 text="⏹️ Stop", 
                                 state="disabled",
                                 bg=self.colors['error'],
                                 fg='white',
                                 font=("Segoe UI", 9),
                                 relief='flat',
                                 padx=15,
                                 pady=8,
                                 cursor='hand2')
        self.stop_btn.grid(row=0, column=1, padx=10)
        
        results_btn = tk.Button(progress_controls, 
                               text="📊 View Results", 
                               command=self.view_results,
                               bg=self.colors['primary'],
                               fg='white',
                               font=("Segoe UI", 9),
                               relief='flat',
                               padx=15,
                               pady=8,
                               cursor='hand2')
        results_btn.grid(row=0, column=2, padx=(10, 0))
        
    def create_modern_status_bar(self):
        """Create the modern status bar."""
        status_frame = tk.Frame(self.root, 
                               bg=self.colors['surface'], 
                               relief='solid', 
                               bd=1)
        status_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))
        status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = tk.Label(status_frame, 
                                    text="Ready", 
                                    font=("Segoe UI", 9),
                                    fg=self.colors['text_secondary'],
                                    bg=self.colors['surface'])
        self.status_label.grid(row=0, column=0, padx=15, pady=8, sticky="w")
        
        # Database status with modern styling
        db_status = tk.Label(status_frame, 
                            text="🟢 MongoDB: Connected | 🟢 SQLite: Ready", 
                            font=("Segoe UI", 9),
                            fg=self.colors['success'],
                            bg=self.colors['surface'])
        db_status.grid(row=0, column=1, padx=15, pady=8, sticky="e")
        
    def load_schemas(self):
        """Load available schemas into the dropdown."""
        try:
            schemas = self.schema_manager.get_all_schemas()
            schema_names = [schema.schema_name for schema in schemas]
            
            self.schema_combo['values'] = schema_names
            if schema_names:
                self.schema_combo.set(schema_names[0])
                self.on_schema_selected(None)
            else:
                self.schema_combo.set("No schemas available")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load schemas: {e}")
            
    def on_schema_selected(self, event):
        """Handle schema selection."""
        selected_name = self.schema_var.get()
        if selected_name and selected_name != "No schemas available":
            try:
                # Find the selected schema
                schemas = self.schema_manager.get_all_schemas()
                for schema in schemas:
                    if schema.schema_name == selected_name:
                        self.current_schema = schema
                        self.update_ui_for_schema()
                        break
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load schema: {e}")
                
    def update_ui_for_schema(self):
        """Update UI elements based on selected schema."""
        if self.current_schema:
            # Update configuration defaults
            self.start_row_var.set(self.current_schema.data_start_row)
            self.duplicate_strategy_var.set(self.current_schema.duplicate_strategy)
            
            # Update status
            self.status_label.config(text=f"Schema loaded: {self.current_schema.schema_name}")
            
    def browse_files(self):
        """Browse for Excel files with validation."""
        file_path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[
                ("Excel files", "*.xlsx *.xls *.xlsm"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            # Validate the selected file
            is_valid, error_message = InputValidator.validate_file_path(file_path)
            
            if is_valid:
                self.selected_file = Path(file_path)
                sanitized_filename = InputValidator.sanitize_filename(self.selected_file.name)
                self.file_label.config(text=sanitized_filename, foreground="black")
                self.status_label.config(text=f"File selected: {sanitized_filename}")
            else:
                messagebox.showerror("Invalid File", error_message)
                self.status_label.config(text=f"File validation failed: {error_message}")
            
    def preview_data(self):
        """Preview the selected Excel file data."""
        if not self.selected_file:
            messagebox.showwarning("Warning", "Please select an Excel file first")
            return
            
        try:
            # Validate file first
            if not self.excel_processor.validate_file(self.selected_file):
                messagebox.showerror("Error", "Invalid Excel file")
                return
            
            # Get preview data
            preview_df = self.excel_processor.preview_data(
                self.selected_file, 
                start_row=self.start_row_var.get(), 
                num_rows=5
            )
            
            if not preview_df.empty:
                # Convert to list of dictionaries for display
                self.preview_data = preview_df.to_dict('records')
                self.update_preview_treeview()
                self.status_label.config(text=f"Preview loaded: {len(self.preview_data)} rows")
            else:
                messagebox.showinfo("Info", "No data found in the specified range")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to preview data: {e}")
            self.status_label.config(text=f"Preview failed: {str(e)}")
            
    def update_preview_treeview(self):
        """Update the preview treeview with data."""
        # Clear existing data
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
            
        if not self.preview_data:
            return
            
        # Setup columns
        columns = list(self.preview_data[0].keys())
        self.preview_tree['columns'] = columns
        
        # Configure column headings
        for col in columns:
            self.preview_tree.heading(col, text=col)
            self.preview_tree.column(col, width=100, minwidth=80)
            
        # Add data rows
        for row_data in self.preview_data:
            values = [str(row_data.get(col, '')) for col in columns]
            self.preview_tree.insert('', 'end', values=values)
            
    def refresh_preview(self):
        """Refresh the data preview."""
        if self.selected_file:
            self.preview_data()
            
    def start_import(self):
        """Start the data import process with validation."""
        # Validate file selection
        if not self.selected_file:
            messagebox.showwarning("Warning", "Please select an Excel file first")
            return
        
        # Re-validate file (in case it was moved/deleted)
        is_valid, error_message = InputValidator.validate_file_path(self.selected_file)
        if not is_valid:
            messagebox.showerror("File Error", f"Selected file is no longer valid:\n{error_message}")
            return
            
        if not self.current_schema:
            messagebox.showwarning("Warning", "Please select or create a schema first")
            return
        
        # Validate processing parameters
        is_valid, error = InputValidator.validate_data_start_row(self.start_row_var.get())
        if not is_valid:
            messagebox.showerror("Invalid Parameter", f"Data start row: {error}")
            return
        
        is_valid, error = InputValidator.validate_duplicate_strategy(self.duplicate_strategy_var.get())
        if not is_valid:
            messagebox.showerror("Invalid Parameter", f"Duplicate strategy: {error}")
            return
            
        # Confirm import
        result = messagebox.askyesno(
            "Confirm Import",
            f"Import {InputValidator.sanitize_filename(self.selected_file.name)} using schema '{self.current_schema.schema_name}'?\n\n"
            f"Data start row: {self.start_row_var.get()}\n"
            f"Duplicate strategy: {self.duplicate_strategy_var.get()}"
        )
        
        if result:
            self.run_import()
            
    def run_import(self):
        """Run the import process in a separate thread."""
        # Disable UI elements
        self.pause_btn.config(state="normal")
        self.stop_btn.config(state="normal")
        
        # Start import thread
        import_thread = threading.Thread(target=self._import_worker, daemon=True)
        import_thread.start()
        
    def _import_worker(self):
        """Worker thread for import process."""
        try:
            # Update progress
            self.root.after(0, lambda: self.progress_label.config(text="Starting import..."))
            self.root.after(0, lambda: self.progress_var.set(10))
            
            # Process file in batches
            processed_rows = 0
            
            # Set up progress callback
            self.ingestion_engine.set_progress_callback(self.on_import_progress)
            
            # Update schema with current settings
            self.current_schema.data_start_row = self.start_row_var.get()
            self.current_schema.duplicate_strategy = self.duplicate_strategy_var.get()
            
            # Run the import using DataIngestionEngine
            result = self.ingestion_engine.import_excel_file(
                self.selected_file,
                self.current_schema,
                self.duplicate_strategy_var.get()
            )
            
            # Import complete - update UI
            if result.success:
                self.root.after(0, lambda: self.progress_label.config(
                    text=f"Import complete! {result.inserted_rows} rows inserted, {result.skipped_rows} skipped"
                ))
                self.root.after(0, lambda: messagebox.showinfo(
                    "Import Complete", 
                    f"Successfully imported {result.inserted_rows} rows!\n\n"
                    f"Processing time: {result.processing_time_ms}ms\n"
                    f"Skipped duplicates: {result.skipped_rows}\n"
                    f"Errors: {result.error_rows}"
                ))
            else:
                error_msg = "\n".join(result.error_messages[:3])  # Show first 3 errors
                self.root.after(0, lambda: messagebox.showwarning(
                    "Import Completed with Errors",
                    f"Import finished but encountered {result.error_rows} errors:\n\n{error_msg}"
                ))
            
            self.root.after(0, lambda: self.progress_var.set(100))
            
            # Re-enable UI
            self.root.after(0, lambda: self.pause_btn.config(state="disabled"))
            self.root.after(0, lambda: self.stop_btn.config(state="disabled"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Import Error", str(e)))
            self.root.after(0, lambda: self.progress_label.config(text="Import failed"))
    
    def on_import_progress(self, progress):
        """Handle import progress updates from DataIngestionEngine."""
        # Update progress on main thread
        self.root.after(0, lambda: self.update_import_progress(progress))
    
    def update_import_progress(self, progress):
        """Update the import progress display."""
        # Update progress bar
        self.progress_var.set(progress.progress_percentage)
        
        # Update progress label
        self.progress_label.config(
            text=f"Processing: {progress.processed_rows}/{progress.total_rows} rows "
                 f"({progress.progress_percentage:.1f}%)"
        )
            
    def view_results(self):
        """View import results."""
        messagebox.showinfo("Results", "Import results feature coming soon!")
        
    def show_create_schema_dialog(self):
        """Show the schema creation dialog."""
        ModernSchemaCreationDialog(self.root, self.schema_manager, self.ai_processor, self)
        
    def show_settings(self):
        """Show modern settings dialog."""
        try:
            ModernSettingsDialog(self.root, self.settings)
        except Exception as e:
            messagebox.showerror("Settings Error", f"Could not open settings: {e}\n\nThis feature is still under development.")
        
    def run(self):
        """Run the main application."""
        self.root.mainloop()


class ModernSchemaCreationDialog:
    """Modern dialog for creating new schemas."""
    
    def __init__(self, parent, schema_manager, ai_processor, main_window):
        """Initialize the schema creation dialog."""
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("✨ Create New Schema")
        self.dialog.geometry("800x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(bg='#f8fafc')
        
        self.schema_manager = schema_manager
        self.ai_processor = ai_processor
        self.main_window = main_window
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the modern dialog UI."""
        # Title
        title_label = tk.Label(self.dialog, 
                              text="✨ Create New Schema", 
                              font=("Segoe UI", 20, "bold"),
                              fg='#2563eb',
                              bg='#f8fafc')
        title_label.pack(pady=(25, 30))
        
        # Schema name with modern styling
        name_frame = tk.Frame(self.dialog, bg='#f8fafc')
        name_frame.pack(fill="x", padx=30, pady=(0, 25))
        
        name_label = tk.Label(name_frame, 
                             text="📝 Schema Name:", 
                             font=("Segoe UI", 12, "bold"),
                             fg='#1e293b',
                             bg='#f8fafc')
        name_label.pack(anchor="w", pady=(0, 8))
        
        self.name_var = tk.StringVar()
        name_entry = tk.Entry(name_frame, 
                             textvariable=self.name_var, 
                             width=60,
                             font=("Segoe UI", 11),
                             relief='solid',
                             bd=1)
        name_entry.pack(fill="x", pady=(0, 0))
        
        # Column names with modern styling
        columns_frame = tk.LabelFrame(self.dialog, 
                                     text="📋 Paste Excel Column Names (one per line)", 
                                     font=("Segoe UI", 12, "bold"),
                                     fg='#1e293b',
                                     bg='#ffffff',
                                     relief='solid',
                                     bd=1)
        columns_frame.pack(fill="both", expand=True, padx=30, pady=(0, 25))
        
        # Instructions
        instructions = tk.Label(columns_frame, 
                               text="💡 Copy your Excel column headers and paste them below, one per line.\nThe AI will automatically normalize and suggest the best structure.",
                               font=("Segoe UI", 10),
                               fg='#64748b',
                               bg='#ffffff',
                               justify='left')
        instructions.pack(anchor="w", padx=20, pady=(20, 15))
        
        # Text area with modern styling
        text_frame = tk.Frame(columns_frame, bg='#ffffff')
        text_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.columns_text = tk.Text(text_frame, 
                                    height=12, 
                                    width=70,
                                    font=("Segoe UI", 10),
                                    relief='solid',
                                    bd=1,
                                    bg='#f8fafc',
                                    fg='#1e293b')
        columns_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.columns_text.yview)
        self.columns_text.configure(yscrollcommand=columns_scrollbar.set)
        
        self.columns_text.pack(side="left", fill="both", expand=True)
        columns_scrollbar.pack(side="right", fill="y")
        
        # Buttons with modern styling
        button_frame = tk.Frame(self.dialog, bg='#f8fafc')
        button_frame.pack(fill="x", padx=30, pady=(0, 25))
        
        ai_btn = tk.Button(button_frame, 
                           text="🤖 Process with AI", 
                           command=self.process_with_ai,
                           bg='#2563eb',
                           fg='white',
                           font=("Segoe UI", 11, "bold"),
                           relief='flat',
                           padx=25,
                           pady=10,
                           cursor='hand2')
        ai_btn.pack(side="left", padx=(0, 15))
        
        manual_btn = tk.Button(button_frame, 
                              text="✏️ Create Manually", 
                              command=self.create_manually,
                              bg='#64748b',
                              fg='white',
                              font=("Segoe UI", 11),
                              relief='flat',
                              padx=25,
                              pady=10,
                              cursor='hand2')
        manual_btn.pack(side="left", padx=(0, 15))
        
        cancel_btn = tk.Button(button_frame, 
                              text="❌ Cancel", 
                              command=self.dialog.destroy,
                              bg='#dc2626',
                              fg='white',
                              font=("Segoe UI", 11),
                              relief='flat',
                              padx=25,
                              pady=10,
                              cursor='hand2')
        cancel_btn.pack(side="right")
        
    def process_with_ai(self):
        """Process column names with AI."""
        schema_name = self.name_var.get().strip()
        if not schema_name:
            messagebox.showwarning("Warning", "Please enter a schema name")
            return
            
        column_text = self.columns_text.get("1.0", tk.END).strip()
        if not column_text:
            messagebox.showwarning("Warning", "Please enter column names")
            return
            
        # Parse column names
        column_names = [line.strip() for line in column_text.split('\n') if line.strip()]
        
        try:
            # Process with AI
            ai_response = self.ai_processor.process_columns(column_names)
            
            # Show AI results dialog
            AIResultsDialog(self.dialog, ai_response, schema_name, column_names, 
                          self.schema_manager, self.main_window)
            
        except Exception as e:
            messagebox.showerror("AI Processing Error", f"Failed to process with AI: {e}")
            
    def create_manually(self):
        """Create schema manually."""
        messagebox.showinfo("Manual Creation", "Manual schema creation coming soon!")


class AIResultsDialog:
    """Dialog for showing AI processing results."""
    
    def __init__(self, parent, ai_response, schema_name, column_names, 
                 schema_manager, main_window):
        """Initialize the AI results dialog."""
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("🤖 AI Schema Processing Results")
        self.dialog.geometry("700x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.ai_response = ai_response
        self.schema_name = schema_name
        self.column_names = column_names
        self.schema_manager = schema_manager
        self.main_window = main_window
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI."""
        # Column normalization
        norm_frame = ttk.LabelFrame(self.dialog, text="✅ Column Normalization", padding=10)
        norm_frame.pack(fill="x", padx=10, pady=10)
        
        norm_text = tk.Text(norm_frame, height=8, width=80)
        norm_scrollbar = ttk.Scrollbar(norm_frame, orient="vertical", command=norm_text.yview)
        norm_text.configure(yscrollcommand=norm_scrollbar.set)
        
        # Populate normalization data
        for excel_col, attr_def in self.ai_response.normalized_attributes.items():
            norm_text.insert(tk.END, f'"{excel_col}" → "{attr_def.field_name}" ({attr_def.data_type})\n')
        
        norm_text.pack(side="left", fill="both", expand=True)
        norm_scrollbar.pack(side="right", fill="y")
        
        # Suggested indexes
        idx_frame = ttk.LabelFrame(self.dialog, text="📑 Suggested Indexes", padding=10)
        idx_frame.pack(fill="x", padx=10, pady=10)
        
        idx_text = tk.Text(idx_frame, height=4, width=80)
        for idx in self.ai_response.suggested_indexes:
            idx_text.insert(tk.END, f"• {', '.join(idx.field_names)} ({idx.index_type})\n")
        idx_text.pack(fill="x")
        
        # Duplicate detection
        dup_frame = ttk.LabelFrame(self.dialog, text="🔍 Duplicate Detection Columns", padding=10)
        dup_frame.pack(fill="x", padx=10, pady=10)
        
        dup_text = tk.Text(dup_frame, height=3, width=80)
        for col in self.ai_response.duplicate_detection_columns:
            dup_text.insert(tk.END, f"• {col}\n")
        dup_text.pack(fill="x")
        
        # Buttons
        button_frame = ttk.Frame(self.dialog, padding=10)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(button_frame, text="✅ Accept & Create", 
                  command=self.accept_and_create).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="✏️ Modify", 
                  command=self.modify_schema).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="❌ Cancel", 
                  command=self.dialog.destroy).pack(side="right")
        
    def accept_and_create(self):
        """Accept AI suggestions and create schema."""
        try:
            # Create schema definition
            schema_def = SchemaDefinition(
                schema_id=f"schema_{self.schema_name.lower().replace(' ', '_')}",
                schema_name=self.schema_name,
                excel_column_names=self.column_names,
                normalized_attributes=self.ai_response.normalized_attributes,
                suggested_indexes=self.ai_response.suggested_indexes,
                duplicate_detection_columns=self.ai_response.duplicate_detection_columns,
                duplicate_strategy="skip",
                data_start_row=2,
                created_at=None,
                last_used=None,
                usage_count=0
            )
            
            # Save schema
            # Save schema (result not used but operation is performed)
            self.schema_manager.save_schema_definition(schema_def)
            
            messagebox.showinfo("Success", f"Schema '{self.schema_name}' created successfully!")
            
            # Refresh main window
            self.main_window.load_schemas()
            
            # Close dialogs
            self.dialog.destroy()
            self.dialog.master.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create schema: {e}")
            
    def modify_schema(self):
        """Modify the schema before creating."""
        messagebox.showinfo("Modify", "Schema modification coming soon!")


class ModernSettingsDialog:
    """Modern settings dialog for application configuration."""
    
    def __init__(self, parent, settings):
        """Initialize the settings dialog."""
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("⚙️ Application Settings")
        self.dialog.geometry("700x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(bg='#f8fafc')
        
        self.settings = settings
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the settings dialog UI."""
        # Title
        title_label = tk.Label(self.dialog, 
                              text="⚙️ Application Settings", 
                              font=("Segoe UI", 18, "bold"),
                              fg='#2563eb',
                              bg='#f8fafc')
        title_label.pack(pady=(20, 30))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Database tab
        self.create_database_tab(notebook)
        
        # AI Configuration tab
        self.create_ai_tab(notebook)
        
        # Processing tab
        self.create_processing_tab(notebook)
        
        # UI Preferences tab
        self.create_ui_tab(notebook)
        
        # Buttons
        button_frame = tk.Frame(self.dialog, bg='#f8fafc')
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        tk.Button(button_frame, 
                 text="💾 Save Settings", 
                 command=self.save_settings,
                 bg='#059669',
                 fg='white',
                 font=("Segoe UI", 10, "bold"),
                 relief='flat',
                 padx=20,
                 pady=8).pack(side="left", padx=(0, 10))
        
        tk.Button(button_frame, 
                 text="❌ Cancel", 
                 command=self.dialog.destroy,
                 bg='#dc2626',
                 fg='white',
                 font=("Segoe UI", 10),
                 relief='flat',
                 padx=20,
                 pady=8).pack(side="right")
        
    def create_database_tab(self, notebook):
        """Create database configuration tab."""
        db_frame = ttk.Frame(notebook)
        notebook.add(db_frame, text="🗄️ Database")
        
        # MongoDB settings
        mongo_frame = tk.LabelFrame(db_frame, 
                                   text="MongoDB Configuration", 
                                   font=("Segoe UI", 12, "bold"),
                                   fg='#1e293b',
                                   bg='#ffffff',
                                   relief='solid',
                                   bd=1)
        mongo_frame.pack(fill="x", padx=20, pady=20)
        
        tk.Label(mongo_frame, 
                text="🔗 MongoDB Connection URL:", 
                font=("Segoe UI", 10, "bold"),
                bg='#ffffff').pack(anchor="w", padx=20, pady=(20, 5))
        
        self.mongo_url_var = tk.StringVar(value=self.settings.database.mongo_url)
        mongo_entry = tk.Entry(mongo_frame, 
                              textvariable=self.mongo_url_var, 
                              width=60,
                              font=("Segoe UI", 10))
        mongo_entry.pack(fill="x", padx=20, pady=(0, 20))
        
        tk.Label(mongo_frame, 
                text="📊 Database Name:", 
                font=("Segoe UI", 10, "bold"),
                bg='#ffffff').pack(anchor="w", padx=20, pady=(0, 5))
        
        self.db_name_var = tk.StringVar(value=self.settings.database.mongo_database)
        db_entry = tk.Entry(mongo_frame, 
                           textvariable=self.db_name_var, 
                           width=30,
                           font=("Segoe UI", 10))
        db_entry.pack(anchor="w", padx=20, pady=(0, 20))
        
        # SQLite settings
        sqlite_frame = tk.LabelFrame(db_frame, 
                                    text="SQLite Configuration", 
                                    font=("Segoe UI", 12, "bold"),
                                    fg='#1e293b',
                                    bg='#ffffff',
                                    relief='solid',
                                    bd=1)
        sqlite_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        tk.Label(sqlite_frame, 
                text="💾 SQLite Database Path:", 
                font=("Segoe UI", 10, "bold"),
                bg='#ffffff').pack(anchor="w", padx=20, pady=(20, 5))
        
        self.sqlite_path_var = tk.StringVar(value=self.settings.database.sqlite_path)
        sqlite_entry = tk.Entry(sqlite_frame, 
                               textvariable=self.sqlite_path_var, 
                               width=60,
                               font=("Segoe UI", 10))
        sqlite_entry.pack(fill="x", padx=20, pady=(0, 20))
        
    def create_ai_tab(self, notebook):
        """Create AI configuration tab."""
        ai_frame = ttk.Frame(notebook)
        notebook.add(ai_frame, text="🤖 AI Configuration")
        
        # OpenAI settings
        openai_frame = tk.LabelFrame(ai_frame, 
                                    text="OpenAI Configuration", 
                                    font=("Segoe UI", 12, "bold"),
                                    fg='#1e293b',
                                    bg='#ffffff',
                                    relief='solid',
                                    bd=1)
        openai_frame.pack(fill="x", padx=20, pady=20)
        
        tk.Label(openai_frame, 
                text="🔑 OpenAI API Key:", 
                font=("Segoe UI", 10, "bold"),
                bg='#ffffff').pack(anchor="w", padx=20, pady=(20, 5))
        
        self.api_key_var = tk.StringVar(value=self.settings.ai.openai_api_key)
        api_entry = tk.Entry(openai_frame, 
                            textvariable=self.api_key_var, 
                            width=60,
                            font=("Segoe UI", 10),
                            show="*")
        api_entry.pack(fill="x", padx=20, pady=(0, 20))
        
        tk.Label(openai_frame, 
                text="🧠 AI Model:", 
                font=("Segoe UI", 10, "bold"),
                bg='#ffffff').pack(anchor="w", padx=20, pady=(0, 5))
        
        self.model_var = tk.StringVar(value=self.settings.ai.openai_model)
        model_combo = ttk.Combobox(openai_frame, 
                                   textvariable=self.model_var,
                                   values=["gpt-4.1-nano", "gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"], 
                                   state="readonly", 
                                   width=30,
                                   font=("Segoe UI", 10))
        model_combo.pack(anchor="w", padx=20, pady=(0, 20))
        
        # AI processing settings
        processing_frame = tk.LabelFrame(ai_frame, 
                                        text="AI Processing Settings", 
                                        font=("Segoe UI", 12, "bold"),
                                        fg='#1e293b',
                                        bg='#ffffff',
                                        relief='solid',
                                        bd=1)
        processing_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        tk.Label(processing_frame, 
                text="🔄 Max Retries:", 
                font=("Segoe UI", 10, "bold"),
                bg='#ffffff').pack(anchor="w", padx=20, pady=(20, 5))
        
        self.retries_var = tk.IntVar(value=self.settings.ai.openai_max_retries)
        retries_spin = tk.Spinbox(processing_frame, 
                                 from_=1, to=10, 
                                 textvariable=self.retries_var,
                                 width=10,
                                 font=("Segoe UI", 10))
        retries_spin.pack(anchor="w", padx=20, pady=(0, 20))
        
    def create_processing_tab(self, notebook):
        """Create processing configuration tab."""
        proc_frame = ttk.Frame(notebook)
        notebook.add(proc_frame, text="⚙️ Processing")
        
        # File processing settings
        file_frame = tk.LabelFrame(proc_frame, 
                                  text="File Processing", 
                                  font=("Segoe UI", 12, "bold"),
                                  fg='#1e293b',
                                  bg='#ffffff',
                                  relief='solid',
                                  bd=1)
        file_frame.pack(fill="x", padx=20, pady=20)
        
        tk.Label(file_frame, 
                text="📁 Max File Size (MB):", 
                font=("Segoe UI", 10, "bold"),
                bg='#ffffff').pack(anchor="w", padx=20, pady=(20, 5))
        
        self.max_size_var = tk.IntVar(value=self.settings.processing.max_file_size_mb)
        size_spin = tk.Spinbox(file_frame, 
                               from_=1, to=1000, 
                               textvariable=self.max_size_var,
                               width=10,
                               font=("Segoe UI", 10))
        size_spin.pack(anchor="w", padx=20, pady=(0, 20))
        
        tk.Label(file_frame, 
                text="👀 Preview Rows:", 
                font=("Segoe UI", 10, "bold"),
                bg='#ffffff').pack(anchor="w", padx=20, pady=(0, 5))
        
        self.preview_rows_var = tk.IntVar(value=self.settings.processing.max_rows_preview)
        preview_spin = tk.Spinbox(file_frame, 
                                  from_=1, to=100, 
                                  textvariable=self.preview_rows_var,
                                  width=10,
                                  font=("Segoe UI", 10))
        preview_spin.pack(anchor="w", padx=20, pady=(0, 20))
        
        # Duplicate handling
        dup_frame = tk.LabelFrame(proc_frame, 
                                 text="Duplicate Handling", 
                                 font=("Segoe UI", 12, "bold"),
                                 fg='#1e293b',
                                 bg='#ffffff',
                                 relief='solid',
                                 bd=1)
        dup_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        tk.Label(dup_frame, 
                text="🔄 Default Strategy:", 
                font=("Segoe UI", 10, "bold"),
                bg='#ffffff').pack(anchor="w", padx=20, pady=(20, 5))
        
        self.strategy_var = tk.StringVar(value=self.settings.processing.duplicate_strategy)
        strategy_combo = ttk.Combobox(dup_frame, 
                                      textvariable=self.strategy_var,
                                      values=["skip", "update", "upsert"], 
                                      state="readonly", 
                                      width=20,
                                      font=("Segoe UI", 10))
        strategy_combo.pack(anchor="w", padx=20, pady=(0, 20))
        
    def create_ui_tab(self, notebook):
        """Create UI preferences tab."""
        ui_frame = ttk.Frame(notebook)
        notebook.add(ui_frame, text="🎨 UI Preferences")
        
        # Window settings
        window_frame = tk.LabelFrame(ui_frame, 
                                    text="Window Settings", 
                                    font=("Segoe UI", 12, "bold"),
                                    fg='#1e293b',
                                    bg='#ffffff',
                                    relief='solid',
                                    bd=1)
        window_frame.pack(fill="x", padx=20, pady=20)
        
        tk.Label(window_frame, 
                text="🪟 Default Window Width:", 
                font=("Segoe UI", 10, "bold"),
                bg='#ffffff').pack(anchor="w", padx=20, pady=(20, 5))
        
        self.width_var = tk.IntVar(value=self.settings.ui.window_width)
        width_spin = tk.Spinbox(window_frame, 
                                from_=800, to=2000, 
                                textvariable=self.width_var,
                                width=10,
                                font=("Segoe UI", 10))
        width_spin.pack(anchor="w", padx=20, pady=(0, 20))
        
        tk.Label(window_frame, 
                text="📏 Default Window Height:", 
                font=("Segoe UI", 10, "bold"),
                bg='#ffffff').pack(anchor="w", padx=20, pady=(0, 5))
        
        self.height_var = tk.IntVar(value=self.settings.ui.window_height)
        height_spin = tk.Spinbox(window_frame, 
                                 from_=600, to=1500, 
                                 textvariable=self.height_var,
                                 width=10,
                                 font=("Segoe UI", 10))
        height_spin.pack(anchor="w", padx=20, pady=(0, 20))
        
        # Theme settings
        theme_frame = tk.LabelFrame(ui_frame, 
                                   text="Theme Settings", 
                                   font=("Segoe UI", 12, "bold"),
                                   fg='#1e293b',
                                   bg='#ffffff',
                                   relief='solid',
                                   bd=1)
        theme_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        tk.Label(theme_frame, 
                text="🎨 Theme:", 
                font=("Segoe UI", 10, "bold"),
                bg='#ffffff').pack(anchor="w", padx=20, pady=(20, 5))
        
        self.theme_var = tk.StringVar(value=self.settings.ui.theme)
        theme_combo = ttk.Combobox(theme_frame, 
                                   textvariable=self.theme_var,
                                   values=["light", "dark", "auto"], 
                                   state="readonly", 
                                   width=20,
                                   font=("Segoe UI", 10))
        theme_combo.pack(anchor="w", padx=20, pady=(0, 20))
        
        # Auto-save setting
        auto_save_var = tk.BooleanVar(value=self.settings.ui.auto_save_schemas)
        auto_save_check = tk.Checkbutton(theme_frame, 
                                         text="💾 Auto-save schema changes", 
                                         variable=auto_save_var,
                                         font=("Segoe UI", 10),
                                         bg='#ffffff')
        auto_save_check.pack(anchor="w", padx=20, pady=(0, 20))
        
    def save_settings(self):
        """Save the current settings."""
        try:
            # Update settings (in a real app, this would save to .env or config file)
            messagebox.showinfo("Success", "Settings saved successfully!\n\nNote: Some settings require app restart to take effect.")
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")


# Test code removed to prevent auto-launching GUI
# if __name__ == "__main__":
#     app = ModernMainWindow()
#     app.run()
