# Credit Risk Model Card (Production Model v2)

## Model Overview
- **Model Architecture**: LightGBM Binary Classifier (`LGBMClassifier`) with Isotonic Probability Calibration (`sklearn.isotonic.IsotonicRegression` with 0.005 probability floor).
- **Date Locked**: 2026-09-21
- **Status**: Production (v2)
- **Objective**: Predict credit default probability (`TARGET` = 1) for loan applicants under fair lending and financial inclusion constraints.

---

## Feature Configuration
- **Final Feature Count**: 17 features
- **Feature List**:
  1. `AMT_INCOME_TOTAL` (Applicant total income)
  2. `AMT_CREDIT` (Credit amount of loan)
  3. `AMT_ANNUITY` (Loan annuity obligation)
  4. `credit_income_ratio` (Loan credit to income ratio)
  5. `annuity_income_ratio` (Monthly payment to income ratio)
  6. `employment_years` (Years of verified employment)
  7. `late_payment_share` (Proportion of past loan payments late)
  8. `mean_days_late` (Average days late on prior payments)
  9. `max_days_late` (Maximum days late on prior payments)
  10. `underpayment_share` (Proportion of past installments underpaid)
  11. `installments_count` (Total count of past completed installments)
  12. `prev_applications_count` (Total count of previous credit applications)
  13. `prev_refused_count` (Count of previous declined credit applications)
  14. `prev_refusal_rate` (Rate of prior credit application refusals)
  15. `thin_file` (Binary indicator: zero prior credit bureau tradelines)
  16. `bureau_active_credits_count` (Count of active bureau credit accounts)
  17. `NAME_INCOME_TYPE` (Income category / source type, label encoded)

---

## Model Performance & Metrics
- **Validation AUC**: 0.67763
- **Calibrated Test AUC**: 0.67796
- **Thin-File Calibrated Test AUC**: 0.67649
- **Thick-File Calibrated Test AUC**: 0.67627
- **Deny / Approve Default Rate Ratio**: 3.98x

---

## Decision Thresholds (Validation-Derived)
- **Approve**: Calibrated Probability $< 0.07474$ (Bottom 60% of score distribution; Actual Default Rate = 4.84%)
- **Refer for Review**: Calibrated Probability $\in [0.07474, 0.13375]$ (Middle 25% of score distribution; Actual Default Rate = 10.44%)
- **Deny**: Calibrated Probability $> 0.13375$ (Top 15% of score distribution; Actual Default Rate = 19.26%)

---

## Fair Lending & Adverse Action Governance
- **Features Excluded from Adverse Action Reason Codes**:
  - `NAME_INCOME_TYPE`: Structural employment category excluded from applicant-facing disclosures per fair lending compliance; audited for disparate impact across demographic segments.
- **Dedup Groups**:
  - `loan_size`: `['AMT_CREDIT', 'credit_income_ratio']` (ensures at most one loan size factor is provided in top 3 reason codes).
  - `credit_history`: `['bureau_active_credits_count']`.

---

## Known Limitations
- `bureau_active_credits_count` is zero-filled for thin-file applicants (who have no prior bureau tradelines).
- SHAP direction for `bureau_active_credits_count` reflects portfolio interaction with thin-file indicator and should be audited independently across sub-segments.
