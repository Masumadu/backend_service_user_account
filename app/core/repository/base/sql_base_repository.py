from typing import Any, Dict, List

from sqlalchemy.exc import DBAPIError, IntegrityError

from app.core.database import Base, db
from app.core.exceptions import AppException

from .crud_repository_interface import CRUDRepositoryInterface


class SQLBaseRepository(CRUDRepositoryInterface):
    model: Base

    def __init__(self):
        """
        Base class to be inherited by all repositories. This class comes with
        base CRUD functionalities attached.

        :param model: Base model of the class to be used for queries.
        """
        self.db = db

    def index(self) -> List[Base]:
        """
        Retrieve all data belonging to a model.

        :return: List of objects of type model.
        :rtype: List[Base]
        :raises AppException.OperationError: If there is an error in the database operation.
        """
        try:
            data = self.db.query(self.model).all()
            return data
        except DBAPIError as exc:
            raise AppException.OperationErrorException(error_message=exc.orig.args[0])

    def create(self, obj_in: Any) -> Base:
        """
        Create a new record.

        :param obj_in: The data you want to use to create the model.
        :return: An instance object of the model passed.
        :rtype: Base
        :raises AppException.OperationError: If there is an error in the database operation.
        :raises AssertionError: If `obj_in` is empty.
        """
        assert obj_in, "Missing data to be saved"

        try:
            obj_data = dict(obj_in)
            db_obj = self.model(**obj_data)
            self.db.add(db_obj)
            self.db.commit()
            return db_obj
        except IntegrityError as exc:
            self.db.rollback()
            raise AppException.OperationErrorException(error_message=exc.orig.args[0])
        except DBAPIError as exc:
            self.db.rollback()
            raise AppException.OperationErrorException(error_message=exc.orig.args[0])

    def update(self, filter_params: Dict[str, Any], obj_in: Dict[str, Any]) -> Base:
        """
        Update the object(s) that match the specified filter parameters with the provided data.

        :param filter_params: Parameters to filter the objects to be updated.
        :type filter_params: Dict[str, Any]
        :param obj_in: Data to update the objects with.
        :type obj_in: Dict[str, Any]
        :return: An instance object of the model passed.
        :rtype: Base
        :raises AppException.OperationError: If there is an error in the database operation.
        """
        db_obj = self.find(filter_params)
        try:
            for field in obj_in:
                if hasattr(db_obj, field):
                    setattr(db_obj, field, obj_in[field])
            self.db.add(db_obj)
            self.db.commit()
            return db_obj
        except DBAPIError as exc:
            self.db.rollback()
            raise AppException.OperationErrorException(error_message=exc.orig.args[0])

    def update_by_id(self, obj_id: str, obj_in: Dict[str, Any]) -> Base:
        """
        Update a record by its ID.

        :param obj_id: ID of the object to update.
        :param obj_in: Update data. This data will be
        used to update any object that matches the specified ID.
        :return: An instance object of the model passed.
        :rtype: Base
        :raises AppException.OperationError: If there is an error
        in the database operation.
        :raises AssertionError: If `obj_id` or `obj_in` is empty,
        or if `obj_in` is not a dictionary.
        """
        assert obj_id, "Missing ID of object to update"
        assert obj_in, "Missing update data"
        assert isinstance(obj_in, dict), "Update data should be a dictionary"

        db_obj = self.find_by_id(obj_id)
        try:
            for field in obj_in:
                if hasattr(db_obj, field):
                    setattr(db_obj, field, obj_in[field])
            self.db.add(db_obj)
            self.db.commit()
            return db_obj
        except DBAPIError as exc:
            self.db.rollback()
            raise AppException.OperationErrorException(error_message=exc.orig.args[0])

    def delete(self, filter_params: Dict[str, Any]) -> None:
        """
        Delete the object(s) that match the specified filter parameters.

        :param filter_params: Parameters to filter the objects to be deleted.
        :type filter_params: Dict[str, Any]
        :return: None
        :raises AppException.OperationError: If there is an error in the database operation.
        """
        db_obj = self.find(filter_params)
        try:
            self.db.delete(db_obj)
            self.db.commit()
        except DBAPIError as exc:
            self.db.rollback()
            raise AppException.OperationErrorException(error_message=exc.orig.args[0])

    def delete_by_id(self, obj_id: str) -> None:
        """
        Delete a record by its ID.

        :param obj_id: ID of the object to delete.
        :raises AppException.OperationError: If there is an error in the database operation.
        :raises AssertionError: If `obj_id` is empty.
        """
        db_obj = self.find_by_id(obj_id)
        try:
            self.db.delete(db_obj)
            self.db.commit()
        except DBAPIError as exc:
            self.db.rollback()
            raise AppException.OperationErrorException(error_message=exc.orig.args[0])

    def find_by_id(self, obj_id: str) -> Base:
        """
        Find an object matching the specified ID if it exists in the database.

        :param obj_id: ID of the object for querying.
        :return: An instance object of the model passed.
        :rtype: Base
        :raises AppException.OperationError: If there is an error in the database operation.
        :raises AssertionError: If `obj_id` is empty.
        """
        assert obj_id, "Missing ID of object for querying"

        try:
            db_obj = self.db.query(self.model).get(obj_id)
            if not db_obj:
                raise AppException.NotFoundException(error_message=None)
            return db_obj
        except DBAPIError as exc:
            raise AppException.OperationErrorException(error_message=exc.orig.args[0])

    def find(self, filter_param: Dict[str, Any]) -> Base:
        """
        Retrieve the first object that matches the specified query parameters.

        :param filter_param: Parameters to be filtered by.
        :type filter_param: Dict[str, Any]
        :return: An instance object of the model passed.
        :rtype: Base
        :raises AppException.OperationError: If there is an error in the database operation.
        :raises AssertionError: If `filter_param` is empty or not of type dictionary.
        """
        assert filter_param, "Missing filter parameters"
        assert isinstance(filter_param, dict), "filter_param should be dict"

        try:
            db_obj = self.db.query(self.model).filter_by(**filter_param).first()
            if not db_obj:
                raise AppException.NotFoundException(error_message=None)
            return db_obj
        except DBAPIError as exc:
            raise AppException.OperationErrorException(error_message=exc.orig.args[0])

    def find_all(self, filter_param: Dict[str, Any]) -> List[Base]:
        """
        Retrieve all objects that match the specified query parameters.

        :param filter_param: Parameters to be filtered by.
        :type filter_param: Dict[str, Any]
        :return: A list of objects of type model.
        :rtype: List[Base]
        :raises AppException.OperationError: If there is an error in the database operation.
        :raises AssertionError: If `filter_param` is empty or not of type dictionary.
        """
        assert filter_param, "Missing filter parameters"
        assert isinstance(filter_param, dict), "filter_param should be dict"

        try:
            db_obj = self.db.query(self.model).filter_by(**filter_param).all()
            return db_obj
        except DBAPIError as exc:
            raise AppException.OperationErrorException(error_message=exc.orig.args[0])
