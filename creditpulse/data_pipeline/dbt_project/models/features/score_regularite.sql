select
    profile_id,
    greatest(0, least(1, historique_paiement)) as score_regularite
from {{ ref('stg_financial_profiles') }}
