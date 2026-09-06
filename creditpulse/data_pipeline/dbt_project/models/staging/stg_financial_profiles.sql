select
    id as profile_id,
        user_id,
        cast(revenu_mensuel as numeric) as revenu_mensuel,
        cast(dettes_actuelles as numeric) as dettes_actuelles,
        cast(age as integer) as age,
        cast(anciennete_emploi as numeric) as anciennete_emploi,
        cast(nombre_credits_en_cours as integer) as nombre_credits_en_cours,
        cast(historique_paiement as numeric) as historique_paiement,
        created_at,
        updated_at
from {{ source('public', 'financial_profiles') }}
where revenu_mensuel is not null
    and revenu_mensuel > 0
    and dettes_actuelles is not null
    and dettes_actuelles >= 0
    and age is not null
    and age > 18
    and anciennete_emploi is not null
    and anciennete_emploi >= 0
    and nombre_credits_en_cours is not null
    and nombre_credits_en_cours >= 0
    and historique_paiement is not null
    and historique_paiement between 0 and 1
