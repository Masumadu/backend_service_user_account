from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Query

from app import constants
from app.core.exceptions import AppException
from app.models import PermissionModel, RoleModel, UserRoleModel
from app.repositories import (
    PermissionRepository,
    RolePermissionRepository,
    RoleRepository,
    UserRepository,
    UserRoleRepository,
)


class RoleController:
    def __init__(
        self,
        role_repository: RoleRepository,
        user_role_repository: UserRoleRepository,
        user_repository: UserRepository,
        permission_repository: PermissionRepository,
        role_permission_repository: RolePermissionRepository,
    ):
        """
        Initialize the RoleController.

        :param role_repository: The role repository.
        :type role_repository: RoleRepository
        :param user_role_repository: The user role repository.
        :type user_role_repository: UserRoleRepository
        :param user_repository: The user repository.
        :type user_repository: UserRepository
        :param permission_repository: The permission repository.
        :type permission_repository: PermissionRepository
        :param role_permission_repository: The role permission repository.
        :type role_permission_repository: RolePermissionRepository
        """
        self.role_repository = role_repository
        self.user_role_repository = user_role_repository
        self.user_repository = user_repository
        self.permission_repository = permission_repository
        self.role_permission_repository = role_permission_repository

    def add_role(self, auth_user: dict, obj_data: dict) -> RoleModel:
        """
        Add a role

        :param auth_user: The authenticated user data.
        :type auth_user: dict
        :param obj_data: The data for the role.
        :type obj_data: dict
        :return: The added role model.
        :rtype: RoleModel
        """
        assert isinstance(obj_data, dict), constants.ASSERT_DICT_OBJECT
        assert obj_data, constants.ASSERT_NULL_OBJECT
        assert auth_user, constants.ASSERT_NULL_OBJECT
        assert isinstance(auth_user, dict), constants.ASSERT_DICT_OBJECT

        user_id: str = auth_user.get("user_id")
        obj_data["created_by"] = user_id
        obj_data["updated_by"] = user_id
        result: RoleModel = self.role_repository.create(obj_in=obj_data)
        return result

    # noinspection PyMethodMayBeStatic
    def view_all_roles(self, **kwargs) -> paginate:
        """
        View all roles.

        :param kwargs: Additional keyword arguments for filtering, sorting, and
                        pagination.Supported keyword arguments:
                       - search: The keyword for searching resources.
                       - sort_in: The field to sort the resources.
                       - order_by: The order of sorting (asc or desc).
                       - paginate: The pagination parameters (page and per_page).
        :type kwargs: any
        :return: The paginated result of roles.
        :rtype: paginate

        :raises AssertionError: If `auth_user` is not a dictionary or if it is empty.
        """

        query_result: Query = RoleModel.search(keyword=kwargs.get("search"))
        query_result: Query = RoleModel.sort(
            query_result=query_result,
            sort_in=kwargs.get("sort_in"),
            order_by=kwargs.get("order_by"),
        )
        result: paginate = RoleModel.paginate(
            query_result=query_result, pagination=kwargs.get("paginate")
        )
        return result

    def view_role(self, obj_id: str) -> RoleModel:
        """
        View a role.

        :param obj_id: The ID of the role.
        :type obj_id: str
        :return: The role model.
        :rtype: RoleModel

        :raises AssertionError: If `auth_user` is not a dictionary or if it is empty.
        :raises AssertionError: If `obj_id` is empty.
        :raises AppException.NotFoundException: If the role is not found.
        """
        assert obj_id, constants.ASSERT_NULL_OBJECT

        try:
            result = self.role_repository.find_by_id(obj_id)
        except AppException.NotFoundException:
            raise AppException.NotFoundException(
                error_message=constants.EXC_NOT_FOUND.format("role")
            )
        return result

    def assign_role_to_user(self, auth_user: dict, obj_data: dict) -> RoleModel:
        """
        Assign a role to a user.

        :param auth_user: The authenticated user data.
        :type auth_user: dict
        :param obj_data: The data for the user-role assignment.
        :type obj_data: dict
        :return: The created user-role model.
        :rtype: RoleModel

        :raises AssertionError: If `obj_data` is not a dictionary or if it is empty.
        :raises AssertionError: If `auth_user` is not a dictionary or if it is empty.
        """
        assert isinstance(obj_data, dict), constants.ASSERT_DICT_OBJECT
        assert obj_data, constants.ASSERT_NULL_OBJECT
        assert auth_user, constants.ASSERT_NULL_OBJECT
        assert isinstance(auth_user, dict), constants.ASSERT_DICT_OBJECT

        user_id: str = auth_user.get("user_id")
        obj_data["created_by"] = user_id
        obj_data["updated_by"] = user_id
        result: UserRoleModel = self.user_role_repository.create(obj_in=obj_data)
        return result.role

    def assign_permission_to_role(
        self, auth_user: dict, obj_data: dict
    ) -> PermissionModel:
        """
        Assign a permission to a role.

        :param auth_user: The authenticated user data.
        :type auth_user: dict
        :param obj_data: The data for the role-permission assignment.
        :type obj_data: dict
        :return: The created role-permission model.
        :rtype: PermissionModel

        :raises AssertionError: If `obj_data` is not a dictionary or if it is empty.
        :raises AssertionError: If `auth_user` is not a dictionary or if it is empty.
        """
        assert isinstance(obj_data, dict), constants.ASSERT_DICT_OBJECT
        assert obj_data, constants.ASSERT_NULL_OBJECT
        assert auth_user, constants.ASSERT_NULL_OBJECT
        assert isinstance(auth_user, dict), constants.ASSERT_DICT_OBJECT

        obj_data["created_by"] = auth_user.get("user_id")
        result: PermissionModel = self.role_permission_repository.create(obj_in=obj_data)
        return result.permission
