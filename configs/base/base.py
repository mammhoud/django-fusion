from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from dynaconf import Dynaconf


class ConfigBase:
    """
    Base configuration class for modular configuration.
    All configuration modules should inherit from this.
    """
    
    def __init__(self, module_name: str, settings: Optional[Dynaconf] = None):
        self.module_name = module_name
        self._settings = settings
        self._config: Dict[str, Any] = {}
        
    def load(self) -> Dict[str, Any]:
        """Load configuration - override in child classes."""
        return {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        if not self._config:
            self._config = self.load()
        return self._config.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        if not self._config:
            self._config = self.load()
        return self._config.copy()
    
    def __call__(self) -> Dict[str, Any]:
        """Make instance callable."""
        return self.to_dict()
    
    def __getitem__(self, key: str) -> Any:
        return self.get(key)
    
    def __contains__(self, key: str) -> bool:
        return key in self.to_dict()
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(module={self.module_name})"
