from typing import Any, Optional, Union

from fastapi.logger import logger


class AppExceptionCase(Exception):
    """
    Base exception to be raised by the application.
    """

    def __init__(
        self, status_code: int, error_message: Any, context: Optional[Any] = None
    ):
        """
        Initialize the AppExceptionCase.

        :param status_code: The status code of the exception.
        :type status_code: int
        :param error_message: The error message.
        :type error_message: Any
        :param context: Other message suitable for troubleshooting errors.
        :type context: Any, optional
        """
        self.exception_case = self.__class__.__name__
        self.status_code = status_code
        self.error_message = error_message
        self.context = context
        logger.critical(self.context) if self.context else None

    def __str__(self):
        """
        Return a string representation of the exception.

        :return: The string representation of the exception.
        :rtype: str
        """
        return (
            f"<AppException {self.exception_case} - "
            + f"status_code = {self.status_code} - error_message = {self.error_message}>"
        )


class AppException:
    """
    The various exceptions that will be raised by the application.
    """

    class OperationErrorException(AppExceptionCase):
        """
        Exception to catch errors caused by failed operations.

        :param error_message: The message returned from the request.
        :type error_message: Any
        :param context: Other message suitable for troubleshooting errors.
        :type context: Any, optional
        """

        def __init__(self, error_message, context=None):
            status_code = 400
            super().__init__(status_code, error_message, context=context)

    class InternalServerException(AppExceptionCase):
        """
        Exception to catch errors caused by server's inability to process an operation.

        :param error_message: The message returned from the request.
        :type error_message: Any
        :param context: Other message suitable for troubleshooting errors.
        :type context: Any, optional
        """

        def __init__(self, error_message, context=None):
            status_code = 500
            super().__init__(status_code, error_message, context=context)

    class ResourceExistsException(AppExceptionCase):
        """
        Exception to catch errors caused by resource duplication.

        :param error_message: The message returned from the request.
        :type error_message: Any
        :param context: Other message suitable for troubleshooting errors.
        :type context: Any, optional
        """

        def __init__(self, error_message, context=None):
            status_code = 409
            super().__init__(status_code, error_message, context=context)

    class NotFoundException(AppExceptionCase):
        """
        Exception to catch errors caused by resource nonexistence.

        :param error_message: The message returned from the request.
        :type error_message: Any
        :param context: Other message suitable for troubleshooting errors.
        :type context: Any, optional
        """

        def __init__(self, error_message: Union[str, None], context=None):
            status_code = 404
            super().__init__(status_code, error_message, context=context)

    class UnauthorizedException(AppExceptionCase):
        """
        Exception to catch errors caused by illegitimate operation.

        :param error_message: The message returned from the request.
        :type error_message: Any
        :param context: Other message suitable for troubleshooting errors.
        :type context: Any, optional
        """

        def __init__(self, error_message, context=None):
            status_code = 401
            super().__init__(status_code, error_message, context=context)

    class ValidationException(AppExceptionCase):
        """
        Exception to catch errors caused by invalid data.

        :param error_message: The message returned from the request.
        :type error_message: Any
        :param context: Other message suitable for troubleshooting errors.
        :type context: Any, optional
        """

        def __init__(self, error_message, context=None):
            status_code = 400
            super().__init__(status_code, error_message, context=context)

    class BadRequestException(AppExceptionCase):
        """
        Exception to catch errors caused by invalid requests.

        :param error_message: The message returned from the request.
        :type error_message: Any
        :param context: Other message suitable for troubleshooting errors.
        :type context: Any, optional
        """

        def __init__(self, error_message, context=None):
            status_code = 400
            super().__init__(status_code, error_message, context=context)

    class InvalidTokenException(AppExceptionCase):
        """
        Exception to catch errors caused by invalid JWT.

        :param error_message: The message returned from the request.
        :type error_message: Any
        :param context: Other message suitable for troubleshooting errors.
        :type context: Any, optional
        """

        def __init__(self, error_message, context=None):
            status_code = 400
            super().__init__(status_code, error_message, context=context)

    class ServiceRequestException(AppExceptionCase):
        """
        Exception to catch errors caused by failure to connect to external services.

        :param error_message: The message returned from the request.
        :type error_message: Any
        :param context: Other message suitable for troubleshooting errors.
        :type context: Any, optional
        """

        def __init__(self, error_message, context=None):
            status_code = 500
            super().__init__(status_code, error_message, context=context)
