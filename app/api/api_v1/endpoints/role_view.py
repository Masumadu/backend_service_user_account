import uuid
from typing import List, Optional

import pinject
from fastapi import APIRouter, Depends, status

from app.controllers import RoleController
from app.enums import SortResultEnum
from app.repositories import (
    PermissionRepository,
    RolePermissionRepository,
    RoleRepository,
    UserRepository,
    UserRoleRepository,
)
from app.schema import (
    AssignRolePermissionSchema,
    AssignUserRoleSchema,
    CreateRoleSchema,
    PermissionSchema,
    RoleSchema,
)
from app.utils import KeycloakJwtAuthentication, Page, Params

role_router = APIRouter()
role_base_url = "/api/v1/roles"
obj_graph = pinject.new_object_graph(
    modules=None,
    classes=[
        RoleController,
        RoleRepository,
        UserRoleRepository,
        UserRepository,
        PermissionRepository,
        RolePermissionRepository,
    ],
)
role_controller: RoleController = obj_graph.provide(RoleController)


@role_router.post("", response_model=RoleSchema, status_code=status.HTTP_201_CREATED)
def add_role(
    obj_data: CreateRoleSchema,
    current_user: dict = Depends(KeycloakJwtAuthentication()),  # noqa
):
    result = role_controller.add_role(current_user, obj_data.dict())
    return result


@role_router.get("", response_model=Page[RoleSchema])
def view_all_roles(
    search: Optional[str] = "",
    sort_in: Optional[SortResultEnum] = SortResultEnum.asc,
    order_by: Optional[str] = None,
    paginate: Params = Depends(),  # noqa
    current_user: dict = Depends(KeycloakJwtAuthentication()),  # noqa
) -> List[RoleSchema]:
    result = role_controller.view_all_roles(
        search=search,
        sort_in=sort_in,
        order_by=order_by,
        paginate=paginate,
    )
    return result


@role_router.get("/{role_id}", response_model=RoleSchema)
def view_role(
    role_id: uuid.UUID, current_user: dict = Depends(KeycloakJwtAuthentication())  # noqa
):
    result = role_controller.view_role(str(role_id))
    return result


@role_router.post("/users", response_model=RoleSchema)
def assign_role_to_user(
    obj_data: AssignUserRoleSchema,
    current_user: dict = Depends(KeycloakJwtAuthentication()),  # noqa
):
    result = role_controller.assign_role_to_user(current_user, obj_data.dict())
    return result


@role_router.post("/permissions", response_model=PermissionSchema)
def assign_permission_to_role(
    obj_data: AssignRolePermissionSchema,
    current_user: dict = Depends(KeycloakJwtAuthentication()),  # noqa
):
    result = role_controller.assign_permission_to_role(current_user, obj_data.dict())
    return result
