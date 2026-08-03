"""
credit.py — Route de demande de crédit (Palier A.2, puis C)

PALIER A (synchrone) :
  POST /credit/apply -> récupère le profil, appelle ml.serve.predict()
                        directement, sauvegarde et retourne le résultat.

PALIER C (event-driven, à remplacer) :
  POST /credit/apply -> publie un événement dans Kafka (topic credit-requests)
                        via app/kafka/producer.py, retourne un statut "pending"
                        avec un id de demande.
  GET  /credit/status/{application_id} -> pour que le frontend poll le résultat
                        une fois traité par le consumer.
"""
