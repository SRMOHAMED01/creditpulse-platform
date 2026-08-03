-- score_regularite.sql — Régularité des paiements historiques (Palier B.1)
-- À IMPLÉMENTER : à partir de l'historique de paiement, calculer un score
-- de régularité (ex : % de paiements à temps sur les 12 derniers mois).

select
    profile_id,
    1 as placeholder -- TODO
from {{ ref('stg_financial_profiles') }}
