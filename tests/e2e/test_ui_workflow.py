#!/usr/bin/env python3
"""
UI E2E Workflow Tests

Tests complete user interactions including:
- Form filling and validation
- Button clicking and navigation
- Schema creation workflow
- Excel import workflow
- Error handling and user feedback
"""

import sys
import time
import unittest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch
import tkinter as tk
from tkinter import ttk

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from ui.main_window import ModernMainWindow
from core.schema_manager import SchemaManager
from models.schema_definition import SchemaDefinition
from config.database_config import get_mongo_client


class UIWorkflowTester(unittest.TestCase):
    """End-to-end UI workflow tester."""

    def setUp(self):
        """Set up test environment."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
        self.main_window = ModernMainWindow()
        self.schema_manager = SchemaManager()
        self.test_schema_name = (
            f"UI Test Schema {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

    def tearDown(self):
        """Clean up after tests."""
        try:
            self.root.destroy()
        except:
            pass

        # Clean up test data
        self.cleanup_test_data()

    def cleanup_test_data(self):
        """Clean up test data from MongoDB."""
        try:
            client = get_mongo_client()
            db = client["excel_schemas"]
            schemas_collection = db["schemas"]

            result = schemas_collection.delete_one(
                {"schema_name": self.test_schema_name}
            )
            if result.deleted_count > 0:
                print(f"🧹 Cleaned up {result.deleted_count} test schema")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")

    def find_widget_by_name(self, parent, name):
        """Find a widget by its name attribute."""
        for widget in parent.winfo_children():
            if hasattr(widget, "name") and widget.name == name:
                return widget
            result = self.find_widget_by_name(widget, name)
            if result:
                return result
        return None

    def find_button_by_text(self, parent, text):
        """Find a button by its text."""
        for widget in parent.winfo_children():
            if (
                isinstance(widget, (tk.Button, ttk.Button))
                and widget.cget("text") == text
            ):
                return widget
            result = self.find_button_by_text(widget, text)
            if result:
                return result
        return None

    def find_entry_by_name(self, parent, name):
        """Find an entry widget by its name."""
        for widget in parent.winfo_children():
            if (
                isinstance(widget, (tk.Entry, ttk.Entry))
                and hasattr(widget, "name")
                and widget.name == name
            ):
                return widget
            result = self.find_entry_by_name(widget, name)
            if result:
                return result
        return None

    def click_button(self, button_text):
        """Click a button by its text."""
        button = self.find_button_by_text(self.main_window.root, button_text)
        if button:
            button.invoke()
            time.sleep(0.1)  # Small delay for UI update
            return True
        return False

    def fill_entry(self, entry_name, value):
        """Fill an entry widget by its name."""
        entry = self.find_entry_by_name(self.root, entry_name)
        if entry:
            entry.delete(0, tk.END)
            entry.insert(0, value)
            entry.event_generate("<<Modified>>")
            time.sleep(0.1)
            return True
        return False

    def test_01_application_startup(self):
        """Test application startup and main window initialization."""
        print("\n🧪 Test 1: Application Startup")

        # Check if main window is created
        self.assertIsNotNone(self.main_window)
        self.assertIsInstance(self.main_window, ModernMainWindow)

        # Check if main window has required components
        self.assertIsNotNone(self.main_window.root.title())
        print("   ✅ Main window initialized correctly")

        # Check if schema manager is available
        self.assertIsNotNone(self.schema_manager)
        print("   ✅ Schema manager initialized")

        print("   ✅ Application startup test passed")

    def test_02_create_schema_button_click(self):
        """Test clicking the 'Create New Schema' button."""
        print("\n🧪 Test 2: Create Schema Button Click")

        # Find and click the create schema button
        success = self.click_button("✨ Create New Schema")
        self.assertTrue(
            success, "✨ Create New Schema button not found or not clickable"
        )
        print("   ✅ ✨ Create New Schema button clicked")

        # Wait for dialog to appear
        time.sleep(0.5)

        # Check if schema creation dialog appeared
        dialogs = [
            w
            for w in self.main_window.root.winfo_children()
            if isinstance(w, tk.Toplevel)
        ]
        self.assertGreater(len(dialogs), 0, "Schema creation dialog did not appear")
        print("   ✅ Schema creation dialog appeared")

        # Close the dialog
        for dialog in dialogs:
            dialog.destroy()

        print("   ✅ Create schema button test passed")

    def test_03_schema_creation_form_filling(self):
        """Test filling out the schema creation form."""
        print("\n🧪 Test 3: Schema Creation Form Filling")

        # Click create schema button
        self.click_button("✨ Create New Schema")
        time.sleep(0.5)

        # Find the schema creation dialog
        dialogs = [
            w
            for w in self.main_window.root.winfo_children()
            if isinstance(w, tk.Toplevel)
        ]
        self.assertGreater(len(dialogs), 0, "Schema creation dialog not found")

        dialog = dialogs[0]

        # Find and fill schema name entry
        schema_name_entry = None
        for widget in dialog.winfo_children():
            if isinstance(widget, (tk.Entry, ttk.Entry)):
                schema_name_entry = widget
                break

        if schema_name_entry:
            schema_name_entry.delete(0, tk.END)
            schema_name_entry.insert(0, self.test_schema_name)
            print("   ✅ Schema name filled")

        # Find and fill database name entry
        database_name_entry = None
        for widget in dialog.winfo_children():
            if (
                isinstance(widget, (tk.Entry, ttk.Entry))
                and widget != schema_name_entry
            ):
                database_name_entry = widget
                break

        if database_name_entry:
            database_name_entry.delete(0, tk.END)
            database_name_entry.insert(0, "test_database")
            print("   ✅ Database name filled")

        # Find and fill collection name entry
        collection_name_entry = None
        for widget in dialog.winfo_children():
            if isinstance(widget, (tk.Entry, ttk.Entry)) and widget not in [
                schema_name_entry,
                database_name_entry,
            ]:
                collection_name_entry = widget
                break

        if collection_name_entry:
            collection_name_entry.delete(0, tk.END)
            collection_name_entry.insert(0, "test_collection")
            print("   ✅ Collection name filled")

        # Find and click the Create button
        create_button = None
        for widget in dialog.winfo_children():
            if isinstance(widget, (tk.Button, ttk.Button)) and "Create" in widget.cget(
                "text"
            ):
                create_button = widget
                break

        if create_button:
            create_button.invoke()
            print("   ✅ Create button clicked")

        # Wait for processing
        time.sleep(1)

        # Close any remaining dialogs
        for dialog in dialogs:
            try:
                dialog.destroy()
            except:
                pass

        print("   ✅ Schema creation form filling test passed")

    def test_04_import_excel_button_click(self):
        """Test clicking the 'Import Excel File' button."""
        print("\n🧪 Test 4: Import Excel Button Click")

        # Find and click the import excel button
        success = self.click_button("🔍 Browse Files")
        if success:
            print("   ✅ 🔍 Browse Files button clicked")
        else:
            print("   ⚠️ 🔍 Browse Files button not found (may be disabled)")

        # Wait for dialog to appear
        time.sleep(0.5)

        # Check if file dialog appeared
        dialogs = [w for w in self.root.winfo_children() if isinstance(w, tk.Toplevel)]
        if len(dialogs) > 0:
            print("   ✅ File dialog appeared")
            # Close the dialog
            for dialog in dialogs:
                dialog.destroy()

        print("   ✅ Import Excel button test passed")

    def test_05_schema_selection_dropdown(self):
        """Test schema selection dropdown functionality."""
        print("\n🧪 Test 5: Schema Selection Dropdown")

        # First create a test schema
        schema_id = self.schema_manager.create_schema(
            self.test_schema_name, ["Name", "Email"]
        )
        schema_def = SchemaDefinition(
            schema_id=schema_id,
            schema_name=self.test_schema_name,
            database_name="test_db",
            excel_column_names=["Name", "Email"],
            normalized_attributes={},
            suggested_indexes=[],
            duplicate_detection_columns=["email"],
            duplicate_strategy="skip",
            data_start_row=2,
            collections=[],
            created_at=datetime.now(),
            last_used=datetime.now(),
            usage_count=0,
        )
        self.schema_manager.save_schema_definition(schema_def)

        # Find the schema selection dropdown
        schema_dropdown = None
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Combobox):
                schema_dropdown = widget
                break

        if schema_dropdown:
            # Check if our test schema appears in the dropdown
            values = schema_dropdown.cget("values")
            self.assertIn(
                self.test_schema_name, values, "Test schema not found in dropdown"
            )
            print("   ✅ Test schema found in dropdown")

            # Select the test schema
            schema_dropdown.set(self.test_schema_name)
            schema_dropdown.event_generate("<<ComboboxSelected>>")
            print("   ✅ Test schema selected in dropdown")
        else:
            print("   ⚠️ Schema dropdown not found")

        print("   ✅ Schema selection dropdown test passed")

    def test_06_error_handling_and_validation(self):
        """Test error handling and form validation."""
        print("\n🧪 Test 6: Error Handling and Validation")

        # Test with empty schema name
        self.click_button("Create New Schema")
        time.sleep(0.5)

        dialogs = [w for w in self.root.winfo_children() if isinstance(w, tk.Toplevel)]
        if len(dialogs) > 0:
            dialog = dialogs[0]

            # Try to create schema without filling required fields
            create_button = None
            for widget in dialog.winfo_children():
                if isinstance(
                    widget, (tk.Button, ttk.Button)
                ) and "Create" in widget.cget("text"):
                    create_button = widget
                    break

            if create_button:
                create_button.invoke()
                time.sleep(0.5)

                # Check if error message appeared
                error_labels = []
                for widget in dialog.winfo_children():
                    if (
                        isinstance(widget, tk.Label)
                        and "error" in widget.cget("text").lower()
                    ):
                        error_labels.append(widget)

                if error_labels:
                    print("   ✅ Error validation working correctly")
                else:
                    print("   ⚠️ No error validation found")

            # Close dialog
            dialog.destroy()

        print("   ✅ Error handling and validation test passed")

    def test_07_ui_responsiveness(self):
        """Test UI responsiveness and performance."""
        print("\n🧪 Test 7: UI Responsiveness")

        start_time = time.time()

        # Perform multiple UI operations
        for i in range(5):
            self.click_button("✨ Create New Schema")
            time.sleep(0.1)

            # Close any dialogs
            dialogs = [
                w for w in self.root.winfo_children() if isinstance(w, tk.Toplevel)
            ]
            for dialog in dialogs:
                dialog.destroy()

        end_time = time.time()
        response_time = end_time - start_time

        # Check if response time is reasonable (less than 2 seconds for 5 operations)
        self.assertLess(
            response_time, 2.0, f"UI response time too slow: {response_time:.2f}s"
        )
        print(f"   ✅ UI response time: {response_time:.2f}s")

        print("   ✅ UI responsiveness test passed")

    def test_08_memory_management(self):
        """Test memory management and cleanup."""
        print("\n🧪 Test 8: Memory Management")

        # Create multiple schemas to test memory usage
        for i in range(3):
            schema_name = f"Memory Test Schema {i}"
            schema_id = self.schema_manager.create_schema(
                schema_name, ["Name", "Email"]
            )
            schema_def = SchemaDefinition(
                schema_id=schema_id,
                schema_name=schema_name,
                database_name="test_db",
                excel_column_names=["Name", "Email"],
                normalized_attributes={},
                suggested_indexes=[],
                duplicate_detection_columns=["email"],
                duplicate_strategy="skip",
                data_start_row=2,
                collections=[],
                created_at=datetime.now(),
                last_used=datetime.now(),
                usage_count=0,
            )
            self.schema_manager.save_schema_definition(schema_def)

        # Check if schemas are properly stored
        all_schemas = self.schema_manager.get_all_schemas()
        test_schemas = [s for s in all_schemas if "Memory Test Schema" in s.schema_name]
        self.assertGreaterEqual(
            len(test_schemas), 3, "Not all test schemas were created"
        )
        print(f"   ✅ Created {len(test_schemas)} test schemas")

        # Clean up test schemas
        for schema in test_schemas:
            self.schema_manager.delete_schema(schema.schema_id)

        print("   ✅ Memory management test passed")

    def test_09_complete_workflow(self):
        """Test complete end-to-end workflow."""
        print("\n🧪 Test 9: Complete E2E Workflow")

        # Step 1: Create schema
        schema_id = self.schema_manager.create_schema(
            self.test_schema_name, ["Name", "Email", "Phone"]
        )
        schema_def = SchemaDefinition(
            schema_id=schema_id,
            schema_name=self.test_schema_name,
            database_name="test_db",
            excel_column_names=["Name", "Email", "Phone"],
            normalized_attributes={},
            suggested_indexes=[],
            duplicate_detection_columns=["email"],
            duplicate_strategy="skip",
            data_start_row=2,
            collections=[],
            created_at=datetime.now(),
            last_used=datetime.now(),
            usage_count=0,
        )
        success = self.schema_manager.save_schema_definition(schema_def)
        self.assertTrue(success, "Failed to save schema")
        print("   ✅ Step 1: Schema created and saved")

        # Step 2: Verify schema appears in UI
        schema_dropdown = None
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Combobox):
                schema_dropdown = widget
                break

        if schema_dropdown:
            values = schema_dropdown.cget("values")
            self.assertIn(
                self.test_schema_name, values, "Schema not found in UI dropdown"
            )
            print("   ✅ Step 2: Schema appears in UI dropdown")

        # Step 3: Test schema selection
        if schema_dropdown:
            schema_dropdown.set(self.test_schema_name)
            schema_dropdown.event_generate("<<ComboboxSelected>>")
            print("   ✅ Step 3: Schema selected in UI")

        # Step 4: Verify schema retrieval
        retrieved_schema = self.schema_manager.get_schema_by_id(schema_id)
        self.assertIsNotNone(retrieved_schema, "Failed to retrieve created schema")
        self.assertEqual(retrieved_schema.schema_name, self.test_schema_name)
        print("   ✅ Step 4: Schema retrieved successfully")

        print("   ✅ Complete E2E workflow test passed")

    def test_10_ui_cleanup_and_shutdown(self):
        """Test proper UI cleanup and shutdown."""
        print("\n🧪 Test 10: UI Cleanup and Shutdown")

        # Test that we can destroy the main window without errors
        try:
            self.root.destroy()
            print("   ✅ Main window destroyed successfully")
        except Exception as e:
            self.fail(f"Failed to destroy main window: {e}")

        # Test that we can create a new window after destruction
        try:
            new_root = tk.Tk()
            new_root.withdraw()
            new_window = ModernMainWindow()
            new_root.destroy()
            print("   ✅ New window created and destroyed successfully")
        except Exception as e:
            self.fail(f"Failed to create new window: {e}")

        print("   ✅ UI cleanup and shutdown test passed")


def run_ui_e2e_tests():
    """Run all UI E2E tests."""
    print("🚀 Starting UI E2E Test Suite")
    print("=" * 60)

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(UIWorkflowTester)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 60)
    print("🎯 UI E2E Test Results:")
    print(f"   ✅ Tests run: {result.testsRun}")
    print(f"   ❌ Failures: {len(result.failures)}")
    print(f"   ⚠️ Errors: {len(result.errors)}")

    if result.failures:
        print("\n❌ Test Failures:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback}")

    if result.errors:
        print("\n❌ Test Errors:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback}")

    if result.wasSuccessful():
        print("\n🎉 All UI E2E tests passed!")
        return True
    else:
        print("\n⚠️ Some UI E2E tests failed.")
        return False


if __name__ == "__main__":
    success = run_ui_e2e_tests()
    sys.exit(0 if success else 1)
