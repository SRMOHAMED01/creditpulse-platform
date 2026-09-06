select
    profile_id,
    round(dettes_actuelles / nullif(revenu_mensuel, 0), 3) as dti_ratio
from {{ ref('stg_financial_profiles') }}
