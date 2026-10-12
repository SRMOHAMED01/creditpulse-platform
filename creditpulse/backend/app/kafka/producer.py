"""
producer.py — Producer Kafka (Palier C.1)
"""

import json
import logging
import os

from confluent_kafka import Producer

logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC_REQUESTS = os.getenv("KAFKA_TOPIC_REQUESTS", "credit-requests")

_producer: Producer | None = None


def get_kafka_producer() -> Producer:
    global _producer
    if _producer is None:
        conf: dict[str, str] = {"bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS}
        try:
            _producer = Producer(conf)
        except Exception:
            logger.exception("Failed to initialize Kafka Producer")
            raise
    return _producer


def delivery_report(err, msg):
    if err is not None:
        logger.error("Message delivery failed: %s", err)
    else:
        logger.info("Message delivered to %s [%d]", msg.topic(), msg.partition())


def publish_credit_request(application_id: int, user_id: int, profile: dict):
    """Publish a credit scoring request to Kafka."""
    producer = get_kafka_producer()
    payload = {
        "application_id": application_id,
        "user_id": user_id,
        "profile": profile,
    }
    producer.produce(
        KAFKA_TOPIC_REQUESTS,
        key=str(application_id),
        value=json.dumps(payload),
        callback=delivery_report,
    )
    producer.flush()
