-- dti_ratio.sql — Debt-to-Income Ratio (Palier B.1)
-- À IMPLÉMENTER : dettes_actuelles / revenu_mensuel, arrondi à 3 décimales,
-- avec une clause pour éviter la division par zéro.

select
    profile_id,
    -- TODO: round(dettes_actuelles::numeric / nullif(revenu_mensuel, 0), 3) as dti_ratio
    1 as placeholder
from {{ ref('stg_financial_profiles') }}
