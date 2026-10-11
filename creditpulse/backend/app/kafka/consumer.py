"""
consumer.py — Consumer Kafka (Palier C.2)
Ce fichier tourne comme un SERVICE SÉPARÉ.
"""

import json
import logging
import os
import sys
from pathlib import Path

from confluent_kafka import Consumer, KafkaError

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.database import SessionLocal
from backend.app.models.credit_application import CreditApplication
from backend.app.models.feature_store import FeatureStore
from ml.serve import predict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC_REQUESTS = os.getenv("KAFKA_TOPIC_REQUESTS", "credit-requests")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "credit-scoring-group")

def process_message(db, payload):
    app_id = payload.get("application_id")
    profile = payload.get("profile")

    logger.info(f"Processing application_id={app_id}")

    # Query feature store if available
    user_id = profile.get("user_id")
    if user_id:
        fs_record = db.query(FeatureStore).filter(FeatureStore.user_id == user_id).first()
        if fs_record:
            profile["dti_ratio"] = fs_record.dti_ratio

    # Call ML model prediction
    prediction = predict(profile)

    # Update CreditApplication in database
    app_record = db.query(CreditApplication).filter(CreditApplication.id == app_id).first()
    if app_record:
        app_record.status = prediction["decision"]
        app_record.score = prediction["score"]
        app_record.explanation = json.dumps(prediction["explanation"])
        db.commit()
        logger.info(f"Application {app_id} updated: status={prediction['decision']}, score={prediction['score']}")

def run_consumer():
    conf = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'group.id': KAFKA_GROUP_ID,
        'auto.offset.reset': 'earliest'
    }

    consumer = Consumer(conf)
    consumer.subscribe([KAFKA_TOPIC_REQUESTS])

    logger.info(f"Kafka Consumer started listening on topic '{KAFKA_TOPIC_REQUESTS}'...")

    db = SessionLocal()
    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    logger.error(f"Kafka error: {msg.error()}")
                    break

            try:
                payload = json.loads(msg.value().decode('utf-8'))
                process_message(db, payload)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    finally:
        db.close()
        consumer.close()

if __name__ == "__main__":
    run_consumer()
