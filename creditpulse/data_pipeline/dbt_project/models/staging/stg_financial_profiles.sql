-- stg_financial_profiles.sql — Nettoyage des données brutes (Palier B.1)
-- À IMPLÉMENTER : SELECT depuis la table source financial_profiles,
-- renommer les colonnes proprement, filtrer les lignes invalides
-- (revenu_mensuel IS NOT NULL AND revenu_mensuel > 0), caster les types.

select
    id as profile_id,
    -- TODO: colonnes nettoyées
    1 as placeholder
from {{ source('public', 'financial_profiles') }}
