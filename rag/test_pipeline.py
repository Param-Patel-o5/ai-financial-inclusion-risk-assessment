import pandas as pd
df = pd.read_parquet('data/demo_pool.parquet')

# Find thin-file applicants who got Approve or Refer
thin_good = df[
    (df['thin_file'] == 1) &
    (df['calib_prob'] < 0.13375)
].head(5)

print(thin_good[[
    'AMT_INCOME_TOTAL','AMT_CREDIT','AMT_ANNUITY',
    'credit_income_ratio','annuity_income_ratio',
    'employment_years','late_payment_share','mean_days_late',
    'max_days_late','underpayment_share','installments_count',
    'prev_applications_count','prev_refused_count',
    'prev_refusal_rate','thin_file','bureau_active_credits_count',
    'NAME_INCOME_TYPE','calib_prob'
]].to_string())