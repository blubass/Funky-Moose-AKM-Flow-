import os
import sys

class Config:
    """Centralized Configuration and Path Management for the Funky Moose Forge."""
    
    APP_NAME = "Funky Moose Release Forge"
    VERSION = "1.0.3"
    YEAR = "2026"
    
    # Paths
    DATA_DIR = os.path.expanduser("~/akm_assistant")
    PROJECTS_DIR = os.path.join(DATA_DIR, "projects")
    DATA_FILE = os.path.join(DATA_DIR, "data.json")
    SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
    BACKUP_FILE = os.path.join(DATA_DIR, "data_backup.json")
    
    # Internal
    ASSETS_DIR = "assets"
    
    @staticmethod
    def get_resource_path(relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    @classmethod
    def ensure_dirs(cls):
        """Creates all necessary data directories."""
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs(cls.PROJECTS_DIR, exist_ok=True)

# Generate Singleton
cfg = Config()
