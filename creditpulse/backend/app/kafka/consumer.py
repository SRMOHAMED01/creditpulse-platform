"""
consumer.py — Consumer Kafka (Palier C.2)
Ce fichier tourne comme un SERVICE SÉPARÉ (process indépendant du serveur
FastAPI), lancé par son propre conteneur Docker dans docker-compose.yml.

À IMPLÉMENTER :
1. Consumer confluent_kafka.Consumer abonné à KAFKA_TOPIC_REQUESTS
2. Boucle infinie : poll() les messages
3. Pour chaque message :
   a. Récupère les features depuis le feature_store (PostgreSQL)
   b. Appelle ml.serve.predict()
   c. Écrit le résultat dans la table credit_applications
   d. Publie un événement sur KAFKA_TOPIC_DECISIONS (optionnel si tu fais
      du WebSocket pour notifier le frontend en direct)

if __name__ == "__main__":
    # run the consume loop
    pass
"""
