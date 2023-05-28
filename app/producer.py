import json

from kafka import KafkaProducer
from kafka.errors import KafkaError

from app.core.exceptions import AppException
from config import settings


def json_serializer(data):
    return json.dumps(data).encode("UTF-8")


def get_partition(key, all, available):
    return 0


def publish_to_kafka(topic, value):
    try:
        producer = KafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers.split("|"),
            value_serializer=json_serializer,
            partitioner=get_partition,
            security_protocol="SASL_PLAINTEXT",
            sasl_mechanism="SCRAM-SHA-256",
            sasl_plain_username=settings.kafka_server_username,
            sasl_plain_password=settings.kafka_server_password,
        )
        producer.send(topic=topic, value=value)
        return True
    except KafkaError as exc:
        raise AppException.OperationError(error_message=f"kafka error with error {exc}")
