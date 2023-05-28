import abc
from typing import Any


class NotificationHandler(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass: Any) -> bool:
        """
        Check if a class is a subclass of NotificationHandler.

        :param subclass: The class to check.
        :type subclass: Any
        :return: True if the class is a subclass of NotificationHandler, False otherwise.
        :rtype: bool
        """
        return (hasattr(subclass, "send")) and callable(subclass.send)

    @abc.abstractmethod
    def send(self):
        """
        Send a notification.

        This method should be implemented by subclasses to define how the notification is sent.
        """
        raise NotImplementedError
