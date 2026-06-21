# ====================================
# 🌐 Network Detection & Environment
# ====================================
import socket

try:
    from core import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


def get_internal_ips() -> list[str]:
    """
    Dynamically determine INTERNAL_IPS based on environment.
    Handles both local and Docker-based development.
    """
    internal_ips = {"127.0.0.1", "10.0.2.2"}  # Vagrant & local Docker default

    try:
        hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
        for ip in ips:
            ip_parts = ip.split(".")
            if len(ip_parts) == 4:
                internal_ips.add(".".join(ip_parts[:3] + ["1"]))
    except Exception:
        pass  # Gracefully fail

    # Add Docker container IPs if applicable
    try:
        # Attempt to resolve Docker "node" container (if exists)
        _, _, docker_ips = socket.gethostbyname_ex("node")
        internal_ips.update(docker_ips)
    except socket.gaierror:
        # Node container not available
        pass

    return list(internal_ips)


# Cached result
INTERNAL_IPS = get_internal_ips()


def get_environment_info() -> dict:
    """
    Get information about the current environment.
    """
    info = {
        'hostname': socket.gethostname(),
        'internal_ips': INTERNAL_IPS,
        'is_docker': False,
    }

    try:
        # Check if running in Docker
        with open('/proc/self/cgroup') as f:
            content = f.read()
            info['is_docker'] = 'docker' in content or '/docker/' in content
    except (FileNotFoundError, PermissionError):
        pass

    return info
