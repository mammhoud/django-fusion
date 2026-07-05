"""
Compatibility shim: enums live in django_fusion.contrib.enums.
Re-exported here for backward compatibility.
Uses direct module imports to avoid triggering django_fusion.__init__ model loading.
"""
import importlib as _importlib

# Import directly from submodules to avoid AppRegistryNotReady
_env = _importlib.import_module("django_fusion.site.enums.env")
_upload = _importlib.import_module("django_fusion.site.enums.upload")

Environment = _env.Environment
Runtime = _env.Runtime
Module = _env.Module
Direction = _env.Direction
Workflow = _env.Workflow
LogLevel = _env.LogLevel

FileUploadStorage = _upload.FileUploadStorage
FileUploadStrategy = _upload.FileUploadStrategy

__all__ = [
    "Environment",
    "Runtime",
    "Module",
    "Direction",
    "Workflow",
    "LogLevel",
    "FileUploadStorage",
    "FileUploadStrategy",
]
