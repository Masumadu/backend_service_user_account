import json
import os
import sys

import pinject
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from loguru import logger

# Add "app" root to PYTHONPATH so we can import from app i.e. from app import create_app.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app  # noqa: E402
from config import settings  # noqa: E402

if __name__ == "__main__":
    logger.info("CONNECTING TO KAFKA SERVER")
    try:
        consumer = KafkaConsumer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            auto_offset_reset="earliest",
            group_id=settings.kafka_consumer_group_id,
            security_protocol="SASL_PLAINTEXT",
            sasl_mechanism="SCRAM-SHA-256",
            sasl_plain_username=settings.kafka_server_username,
            sasl_plain_password=settings.kafka_server_password,
        )
    except KafkaError as exc:
        logger.error(f"failed to consume message on Kafka broker with error {exc}")
    else:
        consumer.subscribe(settings.kafka_subscriptions)
        logger.info(f"Event Subscription List: {settings.kafka_subscriptions}")
        logger.info("AWAITING MESSAGES\n")

        app = create_app()
        # Create Application before importing from app

        from app.controllers import SampleController
        from app.repositories import SampleRepository
        from app.services import RedisService

        for msg in consumer:
            data = json.loads(msg.value)
            logger.info("originating service: service name")
            logger.info(f"topic consuming: {msg.topic}")
            obj_graph = pinject.new_object_graph(
                modules=None,
                classes=[SampleController, SampleRepository, RedisService],
            )
            sample_controller: SampleController = obj_graph.provide(SampleController)
            logger.info("message status: successfully consumed\n")
