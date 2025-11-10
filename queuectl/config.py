"""Configuration management for QueueCTL."""

import json
import os
from pathlib import Path
from typing import Any, Dict


class Config:
    """Manages configuration settings for the queue system."""
    
    DEFAULT_CONFIG = {
        "max_retries": 3,
        "backoff_base": 2,
        "worker_count": 1,
        "data_dir": None,  # Will be set to ~/.queuectl
    }
    
    def __init__(self, config_path: str = None):
        """Initialize configuration.
        
        Args:
            config_path: Path to config file. If None, uses default location.
        """
        if config_path is None:
            home = Path.home()
            self.config_dir = home / ".queuectl"
            self.config_dir.mkdir(exist_ok=True)
            self.config_path = self.config_dir / "config.json"
        else:
            self.config_path = Path(config_path)
            self.config_dir = self.config_path.parent
            self.config_dir.mkdir(exist_ok=True)
        
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Create default config
        config = self.DEFAULT_CONFIG.copy()
        if config["data_dir"] is None:
            config["data_dir"] = str(self.config_dir / "data")
        self._save_config(config)
        return config
    
    def _save_config(self, config: Dict[str, Any] = None):
        """Save configuration to file."""
        if config is None:
            config = self._config
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a configuration value."""
        self._config[key] = value
        self._save_config()
    
    def get_data_dir(self) -> Path:
        """Get the data directory path."""
        data_dir = Path(self._config.get("data_dir", self.config_dir / "data"))
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir
    
    def get_db_path(self) -> Path:
        """Get the database file path."""
        return self.get_data_dir() / "jobs.db"
    
    def get_pid_file(self) -> Path:
        """Get the PID file path for workers."""
        return self.get_data_dir() / "workers.pid"

