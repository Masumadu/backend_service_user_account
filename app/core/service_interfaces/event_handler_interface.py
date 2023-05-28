import abc
from typing import Any


class EventHandlerInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass) -> bool:
        return hasattr(subclass, "handler") and callable(subclass.handler)

    @abc.abstractmethod
    def handler(self, data: Any) -> Any:
        """
        Handles the event data published as a result of an event.

        :param data: The data published as a result of the event.
        :type data: Any
        :return: Any
        """
        raise NotImplementedError
