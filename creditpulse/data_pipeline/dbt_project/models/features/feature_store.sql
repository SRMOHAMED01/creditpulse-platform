select
    profiles.profile_id,
    profiles.user_id,
    profiles.revenu_mensuel,
    profiles.dettes_actuelles,
    profiles.age,
    profiles.anciennete_emploi,
    profiles.nombre_credits_en_cours,
    profiles.historique_paiement,
    dti.dti_ratio,
    regularity.score_regularite,
    profiles.updated_at as profile_updated_at
from {{ ref('stg_financial_profiles') }} as profiles
join {{ ref('dti_ratio') }} as dti
  on dti.profile_id = profiles.profile_id
join {{ ref('score_regularite') }} as regularity
  on regularity.profile_id = profiles.profile_id
