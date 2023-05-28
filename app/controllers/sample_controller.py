from app import constants
from app.core.exceptions import AppException
from app.models import SampleModel
from app.repositories import SampleRepository


class SampleController:
    def __init__(self, sample_repository: SampleRepository):
        self.sample_repository = sample_repository

    # noinspection PyMethodMayBeStatic
    def get_all_resource(self, **kwargs) -> [SampleModel]:
        """
        Get all resource within the system based on the provided keyword arguments
        :param kwargs: the arguments to filter result with
        """

        # reminder: build a query based on the search argument
        query_result = SampleModel.search(keyword=kwargs.get("search"))
        # reminder: apply filters to the search query
        query_result = SampleModel.filter(
            query_result=query_result,
            filter_param={"is_deleted": kwargs.get("is_deleted")},
        )
        # reminder: apply sorting to the filtered query
        query_result = SampleModel.sort(
            query_result=query_result,
            sort_in=kwargs.get("sort_in"),
            sort_by=kwargs.get("sort_by"),
        )
        # reminder: apply pagination to the query and return result
        result = SampleModel.paginate(
            query_result=query_result, pagination=kwargs.get("pagination")
        )
        return result

    def get_resource(self, obj_id: str):
        """
        Get a resource based on the id provided
        :param obj_id: the id of the resource to query for
        """
        assert obj_id, constants.ASSERT_NULL_OBJECT

        try:
            result = self.sample_repository.find_by_id(obj_id)
        except AppException.NotFoundException:
            raise AppException.NotFoundException(error_message="resource does not exist")
        return result

    def create_resource(self, obj_data: dict):
        assert isinstance(obj_data, dict), constants.ASSERT_DICT_OBJECT
        assert obj_data, constants.ASSERT_NULL_OBJECT
        """
        Create a new resource based on the data provided
        :param obj_data: properties of the new resource
        """

        data = self.sample_repository.create(obj_data)
        return data

    def update_resource(self, obj_id: str, obj_data: dict):
        assert isinstance(obj_data, dict), constants.ASSERT_DICT_OBJECT
        assert obj_data, constants.ASSERT_NULL_OBJECT
        assert obj_id, constants.ASSERT_NULL_OBJECT
        """
        Update a resource with id
        :param obj_id: id of the resource to update
        :param obj_data: the data to update resource with
        """

        obj_data = {key: value for key, value in obj_data.items() if value}
        data = self.sample_repository.update_by_id(obj_id, obj_data)
        return data

    def delete(self, obj_id: str):
        assert obj_id, constants.ASSERT_NULL_OBJECT
        """
        Delete a resource with id provided
        :param obj_id: id of the resource to delete
        """
        try:
            self.sample_repository.update_by_id(
                obj_id=obj_id, obj_in={"is_deleted": True}
            )
        except AppException.NotFoundException:
            raise AppException.BadRequest(error_message="resource does not exist")
        return None
