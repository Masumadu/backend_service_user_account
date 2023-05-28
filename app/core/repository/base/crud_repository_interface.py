import abc
from typing import Any


class CRUDRepositoryInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass: Any) -> bool:
        return (
            (hasattr(subclass, "index"))
            and callable(subclass.index)
            and hasattr(subclass, "create")
            and callable(subclass.create)
            and hasattr(subclass, "update_by_id")
            and callable(subclass.update_by_id)
            and hasattr(subclass, "find_by_id")
            and callable(subclass.find_by_id)
            and hasattr(subclass, "delete_by_id")
            and callable(subclass.delete_by_id)
        )

    @abc.abstractmethod
    def index(self) -> Any:
        """
        Retrieve all data belonging to a model.

        :return: Object data.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def create(self, obj_in: Any) -> Any:
        """
        Create a new record.

        :param obj_in: The data to create the model.
        :return: Object data.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def update_by_id(self, obj_id: Any, obj_in: Any) -> Any:
        """
        Update a record by its ID.

        :param obj_id: The ID of the record to update.
        :param obj_in: The data to update the model with.
        :return: A model object.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def find_by_id(self, obj_id: Any) -> Any:
        """
        Find a record by its ID.

        :param obj_id: The ID of the record to find.
        :return: A model object.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete_by_id(self, obj_id: Any) -> Any:
        """
        Delete a record by its ID.

        :param obj_id: The ID of the record to delete.
        :return: A model object.
        """
        raise NotImplementedError
