import uuid
from typing import Optional

import pinject
from fastapi import APIRouter, Depends, status

from app.controllers import ResourceController
from app.enums import SortResultEnum
from app.repositories import PermissionRepository, ResourceRepository
from app.schema import (
    CreateResourceSchema,
    PermissionSchema,
    ResourcePermissionSchema,
    ResourceSchema,
)
from app.utils import KeycloakJwtAuthentication, Page, Params

resource_router = APIRouter()
resource_base_url = "/api/v1/resources"

obj_graph = pinject.new_object_graph(
    modules=None,
    classes=[ResourceController, ResourceRepository, PermissionRepository],
)
resource_controller: ResourceController = obj_graph.provide(ResourceController)


@resource_router.post(
    "", response_model=ResourceSchema, status_code=status.HTTP_201_CREATED
)
def add_resource(
    obj_data: CreateResourceSchema,
    current_user: dict = Depends(KeycloakJwtAuthentication()),  # noqa
) -> ResourceSchema:
    """
    Add a resource.

    :param obj_data: The data for the resource.
    :type obj_data: CreateResourceSchema
    :param current_user: The current authenticated user data.
    :type current_user: dict, optional
    :return: The added resource model.
    :rtype: ResourceSchema
    """
    result = resource_controller.add_resource(current_user, obj_data.dict())
    return result


@resource_router.get("", response_model=Page[ResourceSchema])
def view_all_resources(
    search: Optional[str] = "",
    sort_in: Optional[SortResultEnum] = SortResultEnum.asc,
    order_by: Optional[str] = None,
    paginate: Params = Depends(),  # noqa
    current_user: dict = Depends(KeycloakJwtAuthentication()),  # noqa
):
    """
    View all resources.

    :param search: Search query string (optional).
    :type search: str
    :param sort_in: Sort order (optional).
    :type sort_in: SortResultEnum
    :param order_by: Field to order by (optional).
    :type order_by: str
    :param paginate: Pagination parameters.
    :type paginate: Params
    :param current_user: Current user information.
    :type current_user: dict
    :return: Result of viewing all resources.
    :rtype: [ResourceSchema]
    """
    result = resource_controller.view_all_resource(
        search=search,
        sort_in=sort_in,
        order_by=order_by,
        paginate=paginate,
    )
    return result


@resource_router.get("/{resource_id}", response_model=ResourceSchema)
def view_resource(
    resource_id: uuid.UUID,
    current_user: dict = Depends(KeycloakJwtAuthentication()),  # noqa
) -> ResourceSchema:
    """
    View a resource.

    :param resource_id: The ID of the resource.
    :type resource_id: uuid.UUID
    :param current_user: The current authenticated user data.
    :type current_user: dict
    :return: The resource model.
    :rtype: ResourceSchema

    :raises AppException.NotFoundException: If the resource is not found.
    """
    result = resource_controller.view_resource(str(resource_id))
    return result


@resource_router.post("/permissions", response_model=PermissionSchema)
def assign_permission_to_resource(
    obj_data: ResourcePermissionSchema,
    current_user: dict = Depends(KeycloakJwtAuthentication()),  # noqa
) -> PermissionSchema:
    """
    Assign a permission to a resource.

    :param obj_data: The data for the resource permission.
    :type obj_data: ResourcePermissionSchema
    :param current_user: The current authenticated user data.
    :type current_user: dict
    :return: The permission model.
    :rtype: PermissionSchema

    :raises AppException.NotFoundException: If the resource is not found.
    """
    result = resource_controller.assign_permission_to_resource(
        current_user, obj_data.dict()
    )
    return result
