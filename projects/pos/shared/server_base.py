"""
Backward-compatibility shim — import from shared.api.crud instead.
"""
from shared.api.crud import (  # noqa: F401
    _ser, _ser_node, _paginate, _error,
    _list, _get, _create, _update, _delete, _count,
    _register_crud,
)
