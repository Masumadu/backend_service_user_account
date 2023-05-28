import abc
from typing import Any


class AuthServiceInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass: Any) -> bool:
        return (
            hasattr(subclass, "get_token")
            and callable(subclass.get_token)
            and hasattr(subclass, "refresh_token")
            and callable(subclass.refresh_token)
            and hasattr(subclass, "create_user")
            and callable(subclass.create_user)
            and hasattr(subclass, "update_user")
            and callable(subclass.update_user)
            and hasattr(subclass, "change_password")
            and callable(subclass.change_password)
            and hasattr(subclass, "delete_user")
            and callable(subclass.delete_user)
        )

    @abc.abstractmethod
    def get_token(self, request_data: Any) -> Any:
        """
        Retrieves a valid token based on the provided authentication data.

        :param request_data: Authentication data needed to retrieve a valid token.
        :type request_data: Any
        :return: Any
        """
        raise NotImplementedError

    @abc.abstractmethod
    def refresh_token(self, request_data: Any) -> Any:
        """
        Refreshes the token using the provided refresh token.

        :param request_data: Refresh token needed to get the next valid token.
        :type request_data: Any
        :return: Any
        """
        raise NotImplementedError

    @abc.abstractmethod
    def create_user(self, request_data: Any) -> Any:
        """
        Creates a new user using the provided data.

        :param request_data: Data to create the user with.
        :type request_data: Any
        :return: Any
        """
        raise NotImplementedError

    @abc.abstractmethod
    def update_user(self, request_data: Any) -> Any:
        """
        Updates the user's information using the provided data.

        :param request_data: Data to update the user with.
        :type request_data: Any
        :return: Any
        """
        raise NotImplementedError

    @abc.abstractmethod
    def change_password(self, request_data: Any) -> Any:
        """
        Changes the user's password using the provided data.

        :param request_data: Data to reset the password with.
        :type request_data: Any
        :return: Any
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete_user(self, request_data: Any) -> Any:
        """
        Deletes the user using the provided data.

        :param request_data: Data to delete the user with.
        :type request_data: Any
        :return: Any
        """
        raise NotImplementedError
