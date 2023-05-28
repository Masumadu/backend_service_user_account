import pinject
from fastapi import APIRouter, Depends, status

from app.controllers import SampleController
from app.enums import QuerySortEnum
from app.repositories import SampleRepository
from app.schema import CreateSampleSchema, SampleSchema, UpdateSampleSchema
from app.services import RedisService
from app.utils import (
    KeycloakJwtAuthentication,
    Page,
    Params,
    data_responses,
    query_responses,
)

sample_router = APIRouter()
sample_base_url = "/api/v1/sample-resource"

obj_graph = pinject.new_object_graph(
    modules=None,
    classes=[SampleController, SampleRepository, RedisService],
)
sample_controller: SampleController = obj_graph.provide(SampleController)


@sample_router.get("/", response_model=Page[SampleSchema], responses=query_responses)
def get_all_resource(
    pagination: Params = Depends(),  # noqa
    search: str = "",
    sort_in: QuerySortEnum = QuerySortEnum.asc,
    sort_by: str = None,
    is_deleted: bool = False,
):
    """
    Method for retrieving all resource in the system based on the provided queries
    """

    result = sample_controller.get_all_resource(
        search=search,
        sort_in=sort_in,
        sort_by=sort_by,
        is_deleted=is_deleted,
        pagination=pagination,
    )

    return result


@sample_router.get(
    "/{resource_id}", response_model=SampleSchema, responses=query_responses
)
def get_resource(resource_id: str):
    """
    Method for retrieving a resource based on the resource's id
    """

    result = sample_controller.get_resource(resource_id)
    return result


@sample_router.post(
    "/",
    response_model=SampleSchema,
    status_code=status.HTTP_201_CREATED,
    responses={**data_responses, **query_responses},
)
def create_resource(obj_data: CreateSampleSchema):
    """
    Method for creating a resource
    """

    result = sample_controller.create_resource(obj_data.dict())
    return result


@sample_router.patch(
    "/{resource_id}",
    response_model=SampleSchema,
    responses={**data_responses, **query_responses},
)
def update_resource(
    resource_id: str,
    obj_data: UpdateSampleSchema,
    current_user=Depends(KeycloakJwtAuthentication()),  # noqa
):
    """
    Method for updating a resource based on the resource's id
    """

    result = sample_controller.update_resource(resource_id, obj_data.dict())
    return result


@sample_router.delete(
    "/{resource_id}", status_code=status.HTTP_204_NO_CONTENT, responses=query_responses
)
def delete_resource(
    resource_id: str, current_user=Depends(KeycloakJwtAuthentication())  # noqa
):
    """
    Method for deleting a resource based on the resource's id
    """

    result = sample_controller.delete(resource_id)
    return result
