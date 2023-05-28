import abc
from typing import Any


class CacheServiceInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "set")
            and callable(subclass.set)
            and hasattr(subclass, "get")
            and callable(subclass.get)
            and hasattr(subclass, "delete")
            and callable(subclass.delete)
        )

    @abc.abstractmethod
    def set(self, key: str, data: Any) -> Any:
        """
        Saves the data with the specified key in the cache.

        :param key: The key of the cache object to be saved.
        :type key: str
        :param data: The data to be saved in the cache.
        :type data: Any
        :return: Any
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, key: str) -> Any:
        """
        Retrieves the data associated with the specified key from the cache.

        :param key: The key of the cache object to be retrieved.
        :type key: str
        :return: The data associated with the key, or None if the key does not exist.
        :rtype: Any
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, key: str) -> Any:
        """
        Deletes the cache object with the specified key from the cache.

        :param key: The key of the cache object to be deleted.
        :type key: str
        :return: Any
        """
        raise NotImplementedError
