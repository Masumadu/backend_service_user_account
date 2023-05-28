from typing import Optional

from fastapi import HTTPException as FastApiHTTPException


class HTTPException(FastApiHTTPException):
    def __init__(self, status_code: int, description: Optional[str] = None):
        """
        Custom HTTP exception.

        :param status_code: The HTTP status code.
        :type status_code: int
        :param description: The description of the exception.
        :type description: str, optional
        """
        self.code = status_code
        super(HTTPException, self).__init__(status_code=status_code, detail=description)
