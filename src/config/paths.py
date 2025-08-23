"""
Path Configuration Module

Handles proper Windows user data directory paths for desktop applications.
Follows Windows best practices for data storage and user privacy.
"""

import os
import sys
from pathlib import Path
from typing import Optional


class AppPaths:
    """Manages application paths following Windows best practices."""
    
    def __init__(self, app_name: str = "MoneyFlowV2"):
        """
        Initialize application paths.
        
        Args:
            app_name: Name of the application for directory naming
        """
        self.app_name = app_name
        self._ensure_directories()
    
    @property
    def app_data_roaming(self) -> Path:
        """Get roaming app data directory (persistent across machines)."""
        return Path(os.environ.get('APPDATA', '')) / self.app_name
    
    @property
    def app_data_local(self) -> Path:
        """Get local app data directory (machine-specific)."""
        return Path(os.environ.get('LOCALAPPDATA', '')) / self.app_name
    
    @property
    def user_documents(self) -> Path:
        """Get user documents directory."""
        return Path(os.environ.get('USERPROFILE', '')) / 'Documents' / self.app_name
    
    @property
    def database_dir(self) -> Path:
        """Get database directory (local app data)."""
        return self.app_data_local / 'data'
    
    @property
    def logs_dir(self) -> Path:
        """Get logs directory (local app data)."""
        return self.app_data_local / 'logs'
    
    @property
    def config_dir(self) -> Path:
        """Get configuration directory (roaming app data)."""
        return self.app_data_roaming / 'config'
    
    @property
    def temp_dir(self) -> Path:
        """Get temporary directory (local app data)."""
        return self.app_data_local / 'temp'
    
    @property
    def cache_dir(self) -> Path:
        """Get cache directory (local app data)."""
        return self.app_data_local / 'cache'
    
    @property
    def database_path(self) -> Path:
        """Get full database file path."""
        return self.database_dir / 'templates.db'
    
    @property
    def config_file_path(self) -> Path:
        """Get main configuration file path."""
        return self.config_dir / 'config.json'
    
    @property
    def env_file_path(self) -> Path:
        """Get environment file path."""
        return self.config_dir / '.env'
    
    def _ensure_directories(self) -> None:
        """Create all necessary directories if they don't exist."""
        directories = [
            self.app_data_roaming,
            self.app_data_local,
            self.database_dir,
            self.logs_dir,
            self.config_dir,
            self.temp_dir,
            self.cache_dir,
            self.user_documents
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_log_file_path(self, filename: Optional[str] = None) -> Path:
        """
        Get log file path with optional custom filename.
        
        Args:
            filename: Custom log filename (default: moneyflow_YYYYMMDD.log)
            
        Returns:
            Full path to log file
        """
        if filename is None:
            from datetime import datetime
            filename = f"moneyflow_{datetime.now().strftime('%Y%m%d')}.log"
        
        return self.logs_dir / filename
    
    def get_backup_path(self, original_path: Path, suffix: str = "backup") -> Path:
        """
        Get backup path for a file.
        
        Args:
            original_path: Original file path
            suffix: Backup suffix
            
        Returns:
            Backup file path
        """
        backup_dir = self.app_data_local / 'backups'
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = Path(original_path).stat().st_mtime
        from datetime import datetime
        time_str = datetime.fromtimestamp(timestamp).strftime('%Y%m%d_%H%M%S')
        
        backup_name = f"{original_path.stem}_{time_str}_{suffix}{original_path.suffix}"
        return backup_dir / backup_name
    
    def migrate_old_data(self, old_project_path: Path) -> bool:
        """
        Migrate data from old project directory to new user data directories.
        
        Args:
            old_project_path: Path to old project directory
            
        Returns:
            True if migration successful
        """
        try:
            # Migrate database
            old_db = old_project_path / 'data' / 'templates.db'
            if old_db.exists():
                import shutil
                shutil.copy2(old_db, self.database_path)
                print(f"✅ Migrated database: {old_db} → {self.database_path}")
            
            # Migrate logs
            old_logs = old_project_path / 'logs'
            if old_logs.exists():
                import shutil
                for log_file in old_logs.glob('*.log'):
                    shutil.copy2(log_file, self.logs_dir)
                print(f"✅ Migrated logs: {old_logs} → {self.logs_dir}")
            
            # Migrate config
            old_env = old_project_path / '.env'
            if old_env.exists():
                import shutil
                shutil.copy2(old_env, self.env_file_path)
                print(f"✅ Migrated config: {old_env} → {self.env_file_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False
    
    def cleanup_temp_files(self, max_age_days: int = 7) -> int:
        """
        Clean up old temporary files.
        
        Args:
            max_age_days: Maximum age of files to keep
            
        Returns:
            Number of files cleaned up
        """
        cleaned_count = 0
        current_time = Path().stat().st_mtime
        
        for temp_file in self.temp_dir.glob('*'):
            if temp_file.is_file():
                file_age = current_time - temp_file.stat().st_mtime
                max_age_seconds = max_age_days * 24 * 60 * 60
                
                if file_age > max_age_seconds:
                    temp_file.unlink()
                    cleaned_count += 1
        
        return cleaned_count
    
    def get_relative_path(self, full_path: Path) -> str:
        """
        Get relative path from user data directory.
        
        Args:
            full_path: Full file path
            
        Returns:
            Relative path string
        """
        try:
            return str(full_path.relative_to(self.app_data_local))
        except ValueError:
            try:
                return str(full_path.relative_to(self.app_data_roaming))
            except ValueError:
                return str(full_path)


# Global instance
app_paths = AppPaths()


def get_app_paths() -> AppPaths:
    """Get the global app paths instance."""
    return app_paths


def get_database_path() -> Path:
    """Get the database file path."""
    return app_paths.database_path


def get_logs_directory() -> Path:
    """Get the logs directory path."""
    return app_paths.logs_dir


def get_config_directory() -> Path:
    """Get the configuration directory path."""
    return app_paths.config_dir

