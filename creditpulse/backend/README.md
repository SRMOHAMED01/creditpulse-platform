# backend/ — API FastAPI (Palier A.2, puis C)

Auth JWT, CRUD profil financier, endpoint de demande de crédit.
À partir du Palier C : le endpoint /credit/apply ne calcule plus le score
directement, il publie un événement Kafka (voir app/kafka/).
