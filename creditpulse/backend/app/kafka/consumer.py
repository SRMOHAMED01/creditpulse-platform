"""
consumer.py — Consumer Kafka (Palier C.2)

Runs as a separate service. Listens on the ``credit-requests`` topic,
scores the profile with the XGBoost model, and updates the corresponding
CreditApplication record with the result.
"""

import json
import logging
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

from confluent_kafka import Consumer, KafkaError

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.database import SessionLocal
from backend.app.models.credit_application import CreditApplication
from backend.app.services.ml_service import ScoringUnavailable, predict_credit

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC_REQUESTS = os.getenv("KAFKA_TOPIC_REQUESTS", "credit-requests")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "credit-scoring-group")


def process_message(db, payload: dict) -> bool:
    """Score a credit request and update the application record.

    Returns True if the message was processed successfully.
    """
    app_id = payload.get("application_id")
    profile = payload.get("profile")
    if app_id is None or profile is None:
        logger.error("Invalid payload: %s", payload)
        return False

    logger.info("Processing application_id=%s", app_id)

    record = db.query(CreditApplication).filter(
        CreditApplication.id == app_id
    ).first()
    if record is None:
        logger.error("Application %s not found in database", app_id)
        return False

    try:
        result = predict_credit(profile)
    except ScoringUnavailable:
        logger.error("Scoring unavailable for application %s", app_id)
        record.status = "failed"
        db.commit()
        return False

    record.score = result["score"]
    record.probability_default = result["probability_default"]
    record.decision = result["decision"]
    record.explanation = result["explanation"]
    record.model_version = result["model_version"]
    record.status = "scored"
    record.scored_at = datetime.now(UTC)
    db.commit()
    logger.info(
        "Application %s scored: %s (score=%s, decision=%s)",
        app_id,
        record.status,
        record.score,
        record.decision,
    )
    return True


def run_consumer():
    """Run the Kafka consumer loop."""
    conf = {
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "group.id": KAFKA_GROUP_ID,
        "auto.offset.reset": "earliest",
    }

    consumer = Consumer(conf)
    consumer.subscribe([KAFKA_TOPIC_REQUESTS])

    logger.info("Kafka Consumer started on topic '%s'", KAFKA_TOPIC_REQUESTS)

    db = SessionLocal()
    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                logger.error("Kafka error: %s", msg.error())
                break

            try:
                payload = json.loads(msg.value().decode("utf-8"))
                process_message(db, payload)
            except Exception:
                logger.exception("Error processing message")
    finally:
        db.close()
        consumer.close()


if __name__ == "__main__":
    run_consumer()
