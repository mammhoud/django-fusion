from enum import Enum


class Environment(str, Enum):
    DEVELOPMENT = "development"
    DEMO = "demo"
    PRODUCTION = "production"
    STAGING = "staging"
    TESTING = "testing"


class Runtime(str, Enum):
    LOCAL = "local"
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    CLOUD = "cloud"


class Module(str, Enum):
    LMS = "lms"
    CMS = "cms"
    ECOMMERCE = "ecommerce"
    CRM = "crm"


class Direction(str, Enum):
    SYNC = "sync"


class Workflow(str, Enum):
    STANDARD = "standard"


class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
