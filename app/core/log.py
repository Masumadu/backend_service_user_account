import logging
from datetime import datetime
from logging.handlers import SMTPHandler
from threading import Thread
from typing import Any, Dict, Optional

from config import settings


def get_full_class_name(obj: Any) -> str:
    """
    Get the fully qualified class name of an object.

    :param obj: The object to get the class name from.
    :return: The fully qualified class name.
    :rtype: str
    """
    module = obj.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return obj.__class__.__name__
    return module + "." + obj.__class__.__name__


def get_error_context(
    module: str,
    method: str,
    error: str,
    calling_method: Optional[str] = None,
    calling_module: Optional[str] = None,
    exc_class: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get the error context information.

    :param module: The module where the error occurred.
    :param method: The method where the error occurred.
    :param error: The error message.
    :param calling_method: The method that called the current method (optional).
    :param calling_module: The module that called the current module (optional).
    :param exc_class: The exception class name (optional).
    :return: The error context dictionary.
    :rtype: dict
    """
    return {
        "exception_class": exc_class,
        "module": module,
        "method": method,
        "calling module": calling_module,
        "calling method": calling_method,
        "error": error,
    }


class MailHandler(SMTPHandler):
    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record.

        Format the record and send it to the specified addressees.
        """
        Thread(target=self.send_mail, kwargs={"record": record}).start()

    def send_mail(self, record: logging.LogRecord) -> None:
        """
        Send the log record as an email.

        :param record: The log record to be sent.
        """
        self.timeout = 30
        super().emit(record)


class RequestFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record.

        :param record: The log record to be formatted.
        :return: The formatted log record.
        :rtype: str
        """
        return super().format(record)


def log_config() -> Dict[str, Any]:
    """
    Get the logging configuration.

    :return: The logging configuration dictionary.
    :rtype: dict
    """
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "loggers": {
            "root": {
                "level": "ERROR",
                "handlers": ["console_handler"],
            },
            "gunicorn.error": {
                "handlers": [
                    "console_handler",
                    "error_file_handler",
                    "error_mail_handler",
                ],
                "level": "ERROR",
                "propagate": False,
            },
            "gunicorn.access": {
                "handlers": ["access_file_handler"],
                "level": "INFO",
                "propagate": False,
            },
        },
        "handlers": {
            "console_handler": {
                "level": "ERROR",
                "class": "logging.StreamHandler",
                "formatter": "error_formatter",
                "stream": "ext://sys.stdout",
            },
            "error_mail_handler": {
                "()": "app.core.log.MailHandler",
                "formatter": "error_formatter",
                "level": "ERROR",
                "mailhost": (settings.mail_server, settings.mail_server_port),
                "fromaddr": settings.default_mail_sender_address,
                "toaddrs": settings.admin_mail_addresses,
                "subject": f"{settings.log_header}[{datetime.utcnow().date()}]",
                "credentials": (
                    settings.default_mail_sender_address,
                    settings.default_mail_sender_password,
                ),
                "secure": (),
            },
            "error_file_handler": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "formatter": "error_formatter",
                "level": "ERROR",
                "filename": "gunicorn.error.log",
                "when": "D",
                "interval": 30,
                "backupCount": 1,
            },
            "access_file_handler": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "formatter": "access_formatter",
                "filename": "gunicorn.access.log",
                "when": "D",
                "interval": 30,
                "backupCount": 1,
            },
            "critical_mail_handler": {
                "()": "app.core.log.MailHandler",
                "formatter": "error_formatter",
                "level": "CRITICAL",
                "mailhost": (settings.mail_server, settings.mail_server_port),
                "fromaddr": settings.default_mail_sender_address,
                "toaddrs": settings.admin_mail_addresses,
                "subject": f"{settings.log_header}[{datetime.utcnow().date()}]",
                "credentials": (
                    settings.default_mail_sender_address,
                    settings.default_mail_sender_password,
                ),
                "secure": (),
            },
        },
        "formatters": {
            "access_formatter": {
                "format": "%(message)s",
            },
            "error_formatter": {
                "()": "app.core.log.RequestFormatter",
                "format": """
                \n--- Logging %(levelname)s at %(asctime)s --- \n%(message)s
                """,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
    }
