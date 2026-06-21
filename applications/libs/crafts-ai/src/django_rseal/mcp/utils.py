import subprocess
import tempfile
from pathlib import Path

from django.conf import settings


def get_all_template_dirs():
    """Return list of absolute paths to template directories."""
    dirs = []
    # From TEMPLATES setting
    if hasattr(settings, 'TEMPLATES'):
        for template in settings.TEMPLATES:
            if 'DIRS' in template:
                dirs.extend(template['DIRS'])

    # App template directories
    try:
        from django.template.loaders.app_directories import get_app_template_dirs
        dirs.extend(get_app_template_dirs('templates'))
    except ImportError:
        pass

    # Extra user-defined dirs
    dirs.extend(getattr(settings, 'MCP_EXTRA_TEMPLATE_DIRS', []))

    # Filter unique and existing paths
    unique_dirs = []
    for d in dirs:
        p = Path(d).resolve()
        if p.exists() and p not in unique_dirs:
            unique_dirs.append(p)
    return unique_dirs

def get_all_static_dirs():
    """Return list of absolute paths to static file directories."""
    dirs = []
    # STATICFILES_DIRS
    dirs.extend(getattr(settings, 'STATICFILES_DIRS', []))

    # App static directories
    try:
        from django.contrib.staticfiles.finders import get_finders
        for finder in get_finders():
            if hasattr(finder, 'storages'):
                for storage in finder.storages.values():
                    if hasattr(storage, 'location'):
                        dirs.append(storage.location)
    except Exception:
        pass

    # Extra user-defined dirs
    dirs.extend(getattr(settings, 'MCP_EXTRA_STATIC_DIRS', []))

    # Filter unique and existing paths
    unique_dirs = []
    for d in dirs:
        if not d: continue
        p = Path(d).resolve()
        if p.exists() and p not in unique_dirs:
            unique_dirs.append(p)
    return unique_dirs

def validate_scss(content):
    """Validate SCSS syntax using external command."""
    cmd = getattr(settings, 'MCP_SCSS_CHECK_CMD', 'sass --check')
    with tempfile.NamedTemporaryFile(mode='w', suffix='.scss', delete=False) as f:
        f.write(content)
        tmp = f.name
    try:
        # Check if sass is available
        import shutil
        executable = cmd.split()[0]
        if not shutil.which(executable):
            return  # Skip validation if tool missing

        subprocess.run(cmd.split() + [tmp], check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        raise ValueError(f"SCSS validation failed: {e.stderr.decode()}")
    finally:
        Path(tmp).unlink()
