#!/usr/bin/env python3
"""
Migration Script: Move Data to User Data Directories

This script migrates existing data from the project folder to proper Windows user data directories
following Windows best practices for desktop applications.
"""

import sys
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config.paths import get_app_paths, app_paths


def migrate_data():
    """Migrate data from project folder to user data directories."""
    print("🔄 Starting Data Migration to User Data Directories")
    print("=" * 60)
    
    # Get current project directory
    project_dir = Path(__file__).parent.parent
    print(f"📁 Project directory: {project_dir}")
    
    # Get user data directories
    print(f"📁 User data (roaming): {app_paths.app_data_roaming}")
    print(f"📁 User data (local): {app_paths.app_data_local}")
    
    # Check what needs to be migrated
    old_data_dir = project_dir / "data"
    old_logs_dir = project_dir / "logs"
    old_env_file = project_dir / ".env"
    
    migration_items = []
    
    if old_data_dir.exists():
        migration_items.append(("Database", old_data_dir, app_paths.database_dir))
    
    if old_logs_dir.exists():
        migration_items.append(("Logs", old_logs_dir, app_paths.logs_dir))
    
    if old_env_file.exists():
        migration_items.append(("Config", old_env_file, app_paths.config_dir))
    
    if not migration_items:
        print("✅ No data to migrate - all data already in user directories")
        return True
    
    print(f"\n📋 Found {len(migration_items)} items to migrate:")
    for name, old_path, new_path in migration_items:
        print(f"   - {name}: {old_path} → {new_path}")
    
    # Confirm migration
    print(f"\n⚠️  This will move data from the project folder to user data directories.")
    print(f"   The original files will be backed up before moving.")
    
    try:
        response = input("\nProceed with migration? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("❌ Migration cancelled by user")
            return False
    except KeyboardInterrupt:
        print("\n❌ Migration cancelled by user")
        return False
    
    # Perform migration
    success_count = 0
    total_count = len(migration_items)
    
    for name, old_path, new_path in migration_items:
        try:
            print(f"\n🔄 Migrating {name}...")
            
            if old_path.is_file():
                # Single file migration
                shutil.copy2(old_path, new_path)
                print(f"   ✅ Copied: {old_path.name}")
                
                # Create backup
                backup_path = app_paths.get_backup_path(old_path, "migration")
                shutil.copy2(old_path, backup_path)
                print(f"   💾 Backup created: {backup_path.name}")
                
            elif old_path.is_dir():
                # Directory migration
                new_path.mkdir(parents=True, exist_ok=True)
                
                for item in old_path.iterdir():
                    if item.is_file():
                        shutil.copy2(item, new_path / item.name)
                        print(f"   ✅ Copied: {item.name}")
                
                # Create backup
                backup_dir = app_paths.app_data_local / 'backups' / f"{old_path.name}_migration"
                shutil.copytree(old_path, backup_dir, dirs_exist_ok=True)
                print(f"   💾 Backup created: {backup_dir.name}")
            
            success_count += 1
            print(f"   🎉 {name} migration completed")
            
        except Exception as e:
            print(f"   ❌ {name} migration failed: {e}")
    
    # Summary
    print(f"\n" + "=" * 60)
    print(f"📊 Migration Summary:")
    print(f"   ✅ Successful: {success_count}/{total_count}")
    print(f"   ❌ Failed: {total_count - success_count}/{total_count}")
    
    if success_count == total_count:
        print(f"\n🎉 All data successfully migrated to user data directories!")
        print(f"   📁 Database: {app_paths.database_path}")
        print(f"   📁 Logs: {app_paths.logs_dir}")
        print(f"   📁 Config: {app_paths.config_dir}")
        
        # Ask if user wants to clean up old data
        try:
            cleanup_response = input("\nRemove old data from project folder? (y/N): ").strip().lower()
            if cleanup_response in ['y', 'yes']:
                cleanup_old_data(project_dir, migration_items)
        except KeyboardInterrupt:
            print("\n⏭️  Skipping cleanup")
        
        return True
    else:
        print(f"\n⚠️  Some migrations failed. Check the logs above for details.")
        return False


def cleanup_old_data(project_dir: Path, migration_items):
    """Clean up old data from project folder after successful migration."""
    print(f"\n🧹 Cleaning up old data from project folder...")
    
    for name, old_path, new_path in migration_items:
        try:
            if old_path.is_file():
                old_path.unlink()
                print(f"   ✅ Removed: {old_path}")
            elif old_path.is_dir():
                shutil.rmtree(old_path)
                print(f"   ✅ Removed: {old_path}")
        except Exception as e:
            print(f"   ❌ Failed to remove {old_path}: {e}")
    
    print(f"   🎉 Cleanup completed!")


def verify_migration():
    """Verify that migration was successful."""
    print(f"\n🔍 Verifying migration...")
    
    # Check database
    if app_paths.database_path.exists():
        print(f"   ✅ Database: {app_paths.database_path}")
    else:
        print(f"   ❌ Database not found: {app_paths.database_path}")
    
    # Check logs directory
    if app_paths.logs_dir.exists():
        log_files = list(app_paths.logs_dir.glob("*.log"))
        print(f"   ✅ Logs directory: {app_paths.logs_dir} ({len(log_files)} log files)")
    else:
        print(f"   ❌ Logs directory not found: {app_paths.logs_dir}")
    
    # Check config directory
    if app_paths.config_dir.exists():
        config_files = list(app_paths.config_dir.glob("*"))
        print(f"   ✅ Config directory: {app_paths.config_dir} ({len(config_files)} files)")
    else:
        print(f"   ❌ Config directory not found: {app_paths.config_dir}")


def main():
    """Main migration function."""
    print("🚀 MoneyFlowV2 Data Migration Tool")
    print("=" * 60)
    print("This tool moves your data to proper Windows user data directories.")
    print("This follows Windows best practices and ensures data persistence.")
    print()
    
    try:
        # Perform migration
        success = migrate_data()
        
        if success:
            # Verify migration
            verify_migration()
            
            print(f"\n" + "=" * 60)
            print(f"🎉 Migration completed successfully!")
            print(f"   Your data is now stored in:")
            print(f"   📁 {app_paths.app_data_local}")
            print(f"   📁 {app_paths.app_data_roaming}")
            print(f"\n   The application will now use these locations automatically.")
            
        else:
            print(f"\n❌ Migration failed. Please check the errors above.")
            return 1
            
    except Exception as e:
        print(f"\n💥 Migration failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
