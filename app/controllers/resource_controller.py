from typing import Any, Dict

from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Query

from app import constants
from app.core.exceptions import AppException
from app.models import PermissionModel, ResourceModel
from app.repositories import PermissionRepository, ResourceRepository


class ResourceController:
    """Class responsible for controlling resources."""

    def __init__(
        self,
        resource_repository: ResourceRepository,
        permission_repository: PermissionRepository,
    ) -> None:
        """
        Initialize the ResourceController.

        :param resource_repository: An instance of the ResourceRepository class.
        :param permission_repository: An instance of the PermissionRepository class.
        """
        self.resource_repository = resource_repository
        self.permission_repository = permission_repository

    def add_resource(
        self, auth_user: Dict[str, Any], obj_data: Dict[str, Any]
    ) -> ResourceModel:
        """
        Add a resource.

        :param auth_user: The authenticated user data.
        :type auth_user: dict
        :param obj_data: The data of the object to be created.
        :type obj_data: dict
        :return: The result of the resource creation.
        :rtype: ResourceModel

        :raises AssertionError: If `obj_data` is not a dictionary or is empty.
        :raises AssertionError: If `auth_user` is not a dictionary or is empty.
        """
        assert isinstance(obj_data, dict), constants.ASSERT_DICT_OBJECT
        assert obj_data, constants.ASSERT_NULL_OBJECT
        assert isinstance(auth_user, dict), constants.ASSERT_DICT_OBJECT
        assert auth_user, constants.ASSERT_NULL_OBJECT

        user_id: str = auth_user.get("user_id")
        obj_data["created_by"] = user_id
        obj_data["updated_by"] = user_id
        result: ResourceModel = self.resource_repository.create(obj_in=obj_data)
        return result

    # noinspection PyMethodMayBeStatic
    def view_all_resource(self, **kwargs) -> paginate:
        """
        View all resources.

        :param kwargs: Additional keyword arguments for filtering, sorting, and
                        pagination.Supported keyword arguments:
                       - search: The keyword for searching resources.
                       - sort_in: The field to sort the resources.
                       - order_by: The order of sorting (asc or desc).
                       - paginate: The pagination parameters (page and per_page).
        :type kwargs: any
        :return: The paginated result of resources.
        :rtype: paginate

        :raises AssertionError: If `auth_user` is not a dictionary or if it is empty.
        """
        query_result: Query = ResourceModel.search(keyword=kwargs.get("search"))
        query_result: Query = ResourceModel.sort(
            query_result=query_result,
            sort_in=kwargs.get("sort_in"),
            order_by=kwargs.get("order_by"),
        )
        result: paginate = ResourceModel.paginate(
            query_result=query_result, pagination=kwargs.get("paginate")
        )
        return result

    def view_resource(self, obj_id: str) -> ResourceModel:
        """
        View a resource.

        :param obj_id: The ID of the resource.
        :type obj_id: str
        :return: The resource model.
        :rtype: ResourceModel

        :raises AssertionError: If `auth_user` is not a dictionary or is empty.
        :raises AssertionError: If `obj_id` is empty.
        :raises AppException.NotFoundException: If the resource is not found.
        """
        assert obj_id, constants.ASSERT_NULL_OBJECT

        try:
            result: ResourceModel = self.resource_repository.find_by_id(obj_id)
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                error_message=constants.EXC_NOT_FOUND.format("resource")
            )
        return result

    def assign_permission_to_resource(
        self, auth_user: Dict[str, Any], obj_data: Dict[str, Any]
    ) -> PermissionModel:
        """
        Assign permission to a resource.

        :param auth_user: The authenticated user data.
        :type auth_user: dict
        :param obj_data: The data for assigning the permission.
        :type obj_data: dict
        :return: The result of the permission assignment.
        :rtype: PermissionModel

        :raises AssertionError: If `obj_data` is not a dictionary or is empty.
        :raises AssertionError: If `auth_user` is not a dictionary or is empty.
        """
        assert isinstance(obj_data, dict), constants.ASSERT_DICT_OBJECT
        assert obj_data, constants.ASSERT_NULL_OBJECT
        assert auth_user, constants.ASSERT_NULL_OBJECT
        assert isinstance(auth_user, dict), constants.ASSERT_DICT_OBJECT

        user_id: str = auth_user.get("user_id")
        obj_data["created_by"] = user_id
        obj_data["updated_by"] = user_id
        result: PermissionModel = self.permission_repository.create(obj_in=obj_data)
        return result
