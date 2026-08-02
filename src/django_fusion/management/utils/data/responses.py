"""
HTTP response utility functions for django-fusion.
Provides standardized JSON response helpers.
"""
from typing import Any, Dict

from django.http import JsonResponse


def success_response(data: Dict[str, Any] = None, message: str = "Success", status: int = 200) -> JsonResponse:
    """
    Return standardized success JSON response.

    Args:
        data: Data dictionary to include in response
        message: Success message
        status: HTTP status code (default: 200)

    Returns:
        JsonResponse with standardized success format

    Example:
        >>> success_response({"id": 1, "name": "John"}, "User created")
        JsonResponse({"status": "success", "message": "User created", "data": {"id": 1, "name": "John"}})
    """
    return JsonResponse(
        {
            "status": "success",
            "message": message,
            "data": data or {}
        },
        status=status
    )


def error_response(message: str, errors: Dict[str, Any] = None, status: int = 400) -> JsonResponse:
    """
    Return standardized error JSON response.

    Args:
        message: Error message
        errors: Dictionary of field-specific errors
        status: HTTP status code (default: 400)

    Returns:
        JsonResponse with standardized error format

    Example:
        >>> error_response("Validation failed", {"email": "Invalid format"}, 400)
        JsonResponse({"status": "error", "message": "Validation failed", "errors": {"email": "Invalid format"}})
    """
    return JsonResponse(
        {
            "status": "error",
            "message": message,
            "errors": errors or {}
        },
        status=status
    )


def created_response(data: Dict[str, Any] = None, message: str = "Created successfully") -> JsonResponse:
    """
    Return standardized 201 Created response.

    Args:
        data: Data dictionary to include in response
        message: Success message

    Returns:
        JsonResponse with 201 status

    Example:
        >>> created_response({"id": 1}, "User created")
        JsonResponse({"status": "success", "message": "User created", "data": {"id": 1}}, status=201)
    """
    return success_response(data=data, message=message, status=201)


def not_found_response(message: str = "Resource not found") -> JsonResponse:
    """
    Return standardized 404 Not Found response.

    Args:
        message: Error message

    Returns:
        JsonResponse with 404 status

    Example:
        >>> not_found_response("User not found")
        JsonResponse({"status": "error", "message": "User not found", "errors": {}}, status=404)
    """
    return error_response(message=message, status=404)


def unauthorized_response(message: str = "Authentication required") -> JsonResponse:
    """
    Return standardized 401 Unauthorized response.

    Args:
        message: Error message

    Returns:
        JsonResponse with 401 status

    Example:
        >>> unauthorized_response()
        JsonResponse({"status": "error", "message": "Authentication required", "errors": {}}, status=401)
    """
    return error_response(message=message, status=401)


def forbidden_response(message: str = "Permission denied") -> JsonResponse:
    """
    Return standardized 403 Forbidden response.

    Args:
        message: Error message

    Returns:
        JsonResponse with 403 status

    Example:
        >>> forbidden_response("You don't have permission")
        JsonResponse({"status": "error", "message": "You don't have permission", "errors": {}}, status=403)
    """
    return error_response(message=message, status=403)


def server_error_response(message: str = "Internal server error") -> JsonResponse:
    """
    Return standardized 500 Internal Server Error response.

    Args:
        message: Error message

    Returns:
        JsonResponse with 500 status

    Example:
        >>> server_error_response("Database connection failed")
        JsonResponse({"status": "error", "message": "Database connection failed", "errors": {}}, status=500)
    """
    return error_response(message=message, status=500)


def validation_error_response(errors: Dict[str, Any], message: str = "Validation failed") -> JsonResponse:
    """
    Return standardized validation error response.

    Args:
        errors: Dictionary of field-specific validation errors
        message: General error message

    Returns:
        JsonResponse with 400 status and validation errors

    Example:
        >>> validation_error_response({"email": "Invalid format", "password": "Too short"})
        JsonResponse({"status": "error", "message": "Validation failed", "errors": {...}}, status=400)
    """
    return error_response(message=message, errors=errors, status=400)
