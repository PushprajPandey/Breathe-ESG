import logging

from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import APIException, AuthenticationFailed, NotAuthenticated, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


class BusinessLogicError(APIException):
    status_code = 422
    default_code = "business_error"
    default_detail = "Business logic error."


def _error_payload(code, message, details=None):
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        },
    }


def custom_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)

    if response is not None:
        code = "error"
        message = "An error occurred."
        details = {}

        if isinstance(exc, ValidationError):
            code = "validation_error"
            message = "Validation failed."
            details = response.data
            response.data = _error_payload(code, message, details)
            response.status_code = status.HTTP_400_BAD_REQUEST
        elif isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
            code = "unauthenticated"
            message = str(exc.detail) if hasattr(exc, "detail") else "Authentication required."
            response.data = _error_payload(code, message)
            response.status_code = status.HTTP_401_UNAUTHORIZED
        elif isinstance(exc, PermissionDenied):
            code = "forbidden"
            message = "You do not have permission to perform this action."
            response.data = _error_payload(code, message)
            response.status_code = status.HTTP_403_FORBIDDEN
        elif isinstance(exc, Http404):
            code = "not_found"
            message = "Resource not found."
            response.data = _error_payload(code, message)
            response.status_code = status.HTTP_404_NOT_FOUND
        elif isinstance(exc, BusinessLogicError):
            code = getattr(exc, "default_code", "business_error")
            message = str(exc.detail)
            response.data = _error_payload(code, message)
            response.status_code = 422
        else:
            message = str(exc.detail) if hasattr(exc, "detail") else message
            response.data = _error_payload(code, message)

        return response

    if isinstance(exc, Http404):
        return Response(
            _error_payload("not_found", "Resource not found."),
            status=status.HTTP_404_NOT_FOUND,
        )
    if isinstance(exc, PermissionDenied):
        return Response(
            _error_payload("forbidden", "You do not have permission to perform this action."),
            status=status.HTTP_403_FORBIDDEN,
        )

    logger.exception("Unhandled exception", exc_info=exc)
    return Response(
        _error_payload("server_error", "An unexpected error occurred. Please try again later."),
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
