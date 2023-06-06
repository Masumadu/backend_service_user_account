from fastapi import HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DBAPIError

from .app_exceptions import AppExceptionCase


def exception_message(error: str, message: str, internal_code: int) -> dict:
    """
    Exception message returned by the application when an error occurs.

    :param error: The type of error.
    :param message: The error message.
    :param internal_code: The internal error code.

    :return: A dictionary containing the error information.
    :rtype: dict
    """
    return {"error": error, "message": message, "internal_code": internal_code}


def http_exception_handler(exc: HTTPException) -> JSONResponse:
    """
    Handle HTTP exceptions raised by the application.

    :param exc: The raised exception.
    :type exc: HTTPException

    :return: A JSON response with the error information.
    :rtype: JSONResponse
    """
    return JSONResponse(
        content=exception_message(
            error="HttpException", message=exc.detail, internal_code=exc.status_code
        ),
        status_code=exc.status_code,
        media_type="application/json",
    )


def db_exception_handler(exc: DBAPIError) -> JSONResponse:
    """
    Handle database exceptions raised by the application.

    :param exc: The raised exception.
    :type exc: DBAPIError

    :return: A JSON response with the error information.
    :rtype: JSONResponse
    """
    return JSONResponse(
        content=exception_message(
            error="DatabaseException",
            message=exc.orig.pgerror,
            internal_code=status.HTTP_400_BAD_REQUEST,
        ),
        status_code=status.HTTP_400_BAD_REQUEST,
        media_type="application/json",
    )


def validation_exception_handler(exc: RequestValidationError) -> JSONResponse:
    """
    Handle data validation exceptions raised by the application.

    :param exc: The raised exception.
    :type exc: RequestValidationError

    :return: A JSON response with the error information.
    :rtype: JSONResponse
    """
    fields = [(*error.get("loc"), error.get("msg")) for error in exc.errors()]
    return JSONResponse(
        content=exception_message(
            error="ValidationException",
            message=f"invalid fields {fields}",
            internal_code=status.HTTP_400_BAD_REQUEST,
        ),
        status_code=status.HTTP_400_BAD_REQUEST,
        media_type="application/json",
    )


def app_exception_handler(exc: AppExceptionCase) -> JSONResponse:
    """
    Handle any other exceptions raised by the application.

    :param exc: The raised exception.
    :type exc: AppExceptionCase

    :return: A JSON response with the error information.
    :rtype: JSONResponse
    """
    return JSONResponse(
        content=exception_message(
            error=exc.exception_case,
            message=exc.error_message,
            internal_code=exc.status_code,
        ),
        status_code=exc.status_code,
        media_type="application/json",
    )
