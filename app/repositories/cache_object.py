import json

from fastapi.encoders import jsonable_encoder

from app.core.database import Base
from app.services import RedisService


def obj_serializer(obj_data: Base, cache_key: str, redis_instance: RedisService):
    """
    This function takes a model object, convert it to string and cache it in redis
    :param obj_data: {Model} object to cache
    :param cache_key: {str} name of the object
    :param redis_instance: {RedisService} redis server instance
    :return: {Model} object to cache
    """

    serialize_object = json.dumps(jsonable_encoder(obj_data))
    redis_instance.set(cache_key, serialize_object)

    return obj_data


def objs_serializer(obj_data: Base, cache_key: str, redis_instance: RedisService):
    """
    This function takes a list of model object, convert it to string and cache it in
    redis
    :param obj_data: {list} list of object to cache
    :param cache_key: {str} name of the object
    :param redis_instance: {RedisService} redis server instance
    :return: {Model} object to cache
    """
    serialize_all_object = json.dumps(jsonable_encoder(obj_data))
    redis_instance.set(cache_key, serialize_all_object)
    return obj_data


def obj_deserializer(obj_data: str, obj_model: Base):
    """
    This function takes a cache object, typecast it to a model object
    :param obj_data: {str} object to deserialize
    :param obj_model: {Model} object model to typecast to
    :return: {Model} deserialized object
    """
    deserialized_object = jsonable_encoder(obj_data)

    return obj_model(**deserialized_object)


def objs_deserializer(obj_data: list, obj_model: Base):
    """
    This function takes a list of cache object, typecast it the objects to a model object
    :param obj_data: {list} object to deserialize
    :param obj_model: {Model} object model to typecast
    :return: {list} deserialized object
    """
    deserialize_objects = jsonable_encoder(obj_data)
    for count, value in enumerate(deserialize_objects):
        deserialize_objects[count] = obj_model(**value)

    return deserialize_objects
