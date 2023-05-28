from app.core.exceptions import HTTPException
from app.core.repository import SQLBaseRepository
from app.models import SampleModel
from app.schema import CreateSampleSchema
from app.services import RedisService

from .cache_object import (
    obj_deserializer,
    obj_serializer,
    objs_deserializer,
    objs_serializer,
)

SINGLE_RECORD_CACHE_KEY = "sample_{}_key"
ALL_RECORDS_CACHE_KEY = "all_samples_key"


class SampleRepository(SQLBaseRepository):
    model = SampleModel

    def __init__(self, redis_service: RedisService):
        self.redis_service = redis_service
        super().__init__()

    def index(self):
        try:
            list_of_cached_object = self.redis_service.get(ALL_RECORDS_CACHE_KEY)
            if list_of_cached_object:
                deserialized_objects = objs_deserializer(
                    obj_data=list_of_cached_object,
                    obj_model=self.model,
                )
                return deserialized_objects
            server_data = objs_serializer(
                obj_data=super().index(),
                redis_instance=self.redis_service,
                cache_key=ALL_RECORDS_CACHE_KEY,
            )
            return server_data
        except HTTPException:
            return super().index()

    def create(self, data):
        server_data = super().create(CreateSampleSchema.parse_obj(data))
        try:
            obj_data = obj_serializer(
                obj_data=server_data,
                redis_instance=self.redis_service,
                cache_key=SINGLE_RECORD_CACHE_KEY.format(server_data.id),
            )
            _ = objs_serializer(
                obj_data=super().index(),
                redis_instance=self.redis_service,
                cache_key=ALL_RECORDS_CACHE_KEY,
            )
            return obj_data
        except HTTPException:
            return server_data

    def get_by_id(self, obj_id):
        try:
            cached_object = self.redis_service.get(
                SINGLE_RECORD_CACHE_KEY.format(obj_id)
            )
            if cached_object:
                deserialized_object = obj_deserializer(
                    obj_data=cached_object,
                    obj_model=self.model,
                )
                return deserialized_object
            object_data = obj_serializer(
                obj_data=super().find_by_id(obj_id),
                redis_instance=self.redis_service,
                cache_key=SINGLE_RECORD_CACHE_KEY.format(obj_id),
            )
            return object_data
        except HTTPException:
            return super().find_by_id(obj_id)

    def update_by_id(self, obj_id: str, obj_in: dict):
        postgres_data = super().update_by_id(obj_id, obj_in)
        try:
            redis_data = self.redis_service.get(SINGLE_RECORD_CACHE_KEY.format(obj_id))
            if redis_data:
                self.redis_service.delete(SINGLE_RECORD_CACHE_KEY.format(obj_id))
            object_data = obj_serializer(
                obj_data=postgres_data,
                redis_instance=self.redis_service,
                cache_key=SINGLE_RECORD_CACHE_KEY.format(postgres_data.id),
            )
            _ = objs_serializer(
                obj_data=super().index(),
                redis_instance=self.redis_service,
                cache_key=ALL_RECORDS_CACHE_KEY,
            )
            return object_data
        except HTTPException:
            return super().update_by_id(obj_id, obj_in)

    def delete_by_id(self, obj_id):
        postgres_data = super().delete_by_id(obj_id)
        try:
            redis_data = self.redis_service.get(SINGLE_RECORD_CACHE_KEY.format(obj_id))
            if redis_data:
                self.redis_service.delete(SINGLE_RECORD_CACHE_KEY.format(obj_id))
            _ = objs_serializer(
                obj_data=super().index(),
                redis_instance=self.redis_service,
                cache_key=ALL_RECORDS_CACHE_KEY,
            )
            return postgres_data
        except HTTPException:
            return super().delete_by_id(obj_id)
