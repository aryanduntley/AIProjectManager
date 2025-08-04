"""
Configuration manager for the AI Project Manager MCP Server.

Handles loading and validation of user settings and server configuration.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)


class LoggingConfig(BaseModel):
    """Configuration for logging settings."""
    enabled: bool = True
    level: str = "INFO"
    retention_days: int = 30
    max_file_size: str = "10MB"


class ProjectConfig(BaseModel):
    """Configuration for project management settings."""
    max_file_lines: int = 900
    auto_modularize: bool = True
    theme_discovery: bool = True
    backup_enabled: bool = True
    management_folder_name: str = "projectManagement"


class ServerConfig(BaseModel):
    """Main configuration model."""
    logging: LoggingConfig = LoggingConfig()
    project: ProjectConfig = ProjectConfig()
    debug: bool = False
    version: str = "1.0.0"


class ConfigManager:
    """Manages configuration loading and validation."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.cwd()
        self.config: ServerConfig = ServerConfig()
        self._config_loaded = False
    
    async def load_config(self, config_path: Optional[Path] = None) -> ServerConfig:
        """Load configuration from file or environment variables."""
        try:
            # Try to load from file first
            if config_path:
                config_file = config_path
            else:
                # Look for config in various locations
                possible_paths = [
                    self.config_dir / "config.json",
                    Path.home() / ".ai-project-manager" / "config.json",
                    Path("/etc/ai-project-manager/config.json")
                ]
                
                config_file = None
                for path in possible_paths:
                    if path.exists():
                        config_file = path
                        break
            
            if config_file and config_file.exists():
                logger.info(f"Loading configuration from {config_file}")
                config_data = await self._load_config_file(config_file)
                self.config = ServerConfig(**config_data)
            else:
                logger.info("No configuration file found, using defaults")
                self.config = ServerConfig()
            
            # Override with environment variables
            self._load_env_overrides()
            
            self._config_loaded = True
            logger.info("Configuration loaded successfully")
            return self.config
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            # Fall back to defaults
            self.config = ServerConfig()
            self._config_loaded = True
            return self.config
    
    async def _load_config_file(self, config_path: Path) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
            
            # Handle template format where managementFolderName is under 'project'
            if 'project' in data and 'managementFolderName' in data['project']:
                # Convert template format to config format
                if 'project' not in data or 'management_folder_name' not in data['project']:
                    data.setdefault('project', {})['management_folder_name'] = data['project']['managementFolderName']
            
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file {config_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error reading config file {config_path}: {e}")
            raise
    
    def _load_env_overrides(self):
        """Load configuration overrides from environment variables."""
        env_mappings = {
            "AI_PM_DEBUG": ("debug", bool),
            "AI_PM_MAX_FILE_LINES": ("project.max_file_lines", int),
            "AI_PM_LOG_LEVEL": ("logging.level", str),
            "AI_PM_LOG_RETENTION": ("logging.retention_days", int),
            "AI_PM_MANAGEMENT_FOLDER": ("project.management_folder_name", str),
        }
        
        for env_var, (config_path, value_type) in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                try:
                    # Convert value to appropriate type
                    if value_type == bool:
                        converted_value = env_value.lower() in ('true', '1', 'yes', 'on')
                    elif value_type == int:
                        converted_value = int(env_value)
                    else:
                        converted_value = env_value
                    
                    # Set the configuration value
                    self._set_nested_config(config_path, converted_value)
                    logger.debug(f"Override from {env_var}: {config_path} = {converted_value}")
                    
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid value for {env_var}: {env_value} ({e})")
    
    def _set_nested_config(self, path: str, value: Any):
        """Set a nested configuration value using dot notation."""
        parts = path.split('.')
        current = self.config
        
        # Navigate to the parent of the target attribute
        for part in parts[:-1]:
            current = getattr(current, part)
        
        # Set the final attribute
        setattr(current, parts[-1], value)
    
    def get_config(self) -> ServerConfig:
        """Get the current configuration."""
        if not self._config_loaded:
            raise RuntimeError("Configuration not loaded. Call load_config() first.")
        return self.config
    
    def get_project_config(self) -> ProjectConfig:
        """Get project-specific configuration."""
        return self.get_config().project
    
    def get_logging_config(self) -> LoggingConfig:
        """Get logging-specific configuration."""
        return self.get_config().logging
    
    def get_management_folder_name(self) -> str:
        """Get the configured management folder name."""
        return self.get_config().project.management_folder_name
    
    async def save_config(self, config_path: Optional[Path] = None):
        """Save current configuration to file."""
        if not config_path:
            config_path = self.config_dir / "config.json"
        
        try:
            # Ensure directory exists
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert config to dict and save
            config_dict = self.config.model_dump()
            with open(config_path, 'w') as f:
                json.dump(config_dict, f, indent=2)
            
            logger.info(f"Configuration saved to {config_path}")
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            raise
    
    def validate_config(self) -> bool:
        """Validate the current configuration."""
        try:
            # Pydantic models automatically validate on creation
            # Additional custom validation can be added here
            config = self.get_config()
            
            # Check that max_file_lines is reasonable
            if config.project.max_file_lines < 100:
                logger.warning("max_file_lines is very low, this may cause excessive modularization")
            
            if config.project.max_file_lines > 5000:
                logger.warning("max_file_lines is very high, this may cause performance issues")
            
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False