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

_producer = None

def get_kafka_producer():
    global _producer
    if _producer is None:
        conf = {'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS}
        try:
            _producer = Producer(conf)
        except Exception as e:
            logger.error(f"Failed to initialize Kafka Producer: {e}")
            raise e
    return _producer

def delivery_report(err, msg):
    if err is not None:
        logger.error(f"Message delivery failed: {err}")
    else:
        logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def publish_credit_request(application_id: int, profile: dict):
    producer = get_kafka_producer()
    payload = {
        "application_id": application_id,
        "profile": profile
    }
    producer.produce(
        KAFKA_TOPIC_REQUESTS,
        key=str(application_id),
        value=json.dumps(payload),
        callback=delivery_report
    )
    producer.flush()
