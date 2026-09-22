# Credit Risk Model Card (Production Model v3)

## Model Overview
- **Model Architecture**: LightGBM Binary Classifier (`LGBMClassifier`) with Isotonic Probability Calibration (`sklearn.isotonic.IsotonicRegression` with 0.005 probability floor).
- **Date Locked**: 2026-09-23
- **Status**: Production (v3 with High-AUC Predictive Layer & Two-Tier Feature Gating)
- **Objective**: Predict credit default probability (`TARGET` = 1) for loan applicants under fair lending, financial inclusion, and adverse action compliance constraints.

---

## Feature Configuration

### Total Features (20 features)
1. `AMT_INCOME_TOTAL` (Applicant total annual income)
2. `AMT_CREDIT` (Requested credit amount)
3. `AMT_ANNUITY` (Annual loan repayment annuity)
4. `credit_income_ratio` (Requested credit / annual income)
5. `annuity_income_ratio` (Annuity payment / annual income)
6. `employment_years` (Years of verified employment)
7. `late_payment_share` (Proportion of past loan payments late)
8. `mean_days_late` (Average days late on prior payments)
9. `max_days_late` (Maximum days late on prior payments)
10. `underpayment_share` (Proportion of past installments underpaid)
11. `installments_count` (Total completed installment count)
12. `prev_applications_count` (Prior credit application count)
13. `prev_refused_count` (Prior declined credit application count)
14. `prev_refusal_rate` (Rate of prior credit application refusals)
15. `thin_file` (Binary indicator: zero prior credit bureau tradelines)
16. `bureau_active_credits_count` (Count of active bureau credit accounts)
17. `EXT_SOURCE_2` (Normalized external credit bureau aggregator score)
18. `EXT_SOURCE_3` (Normalized external risk bureau score)
19. `mobile_bill_consistency` (Alternative telecom / recurring utility payment consistency score)
20. `AMT_REQ_CREDIT_BUREAU_YEAR` (Annual credit bureau inquiry volume)

---

## Model Performance & Metrics

- **Best Iteration**: 184
- **Validation AUC**: 0.74006
- **Calibrated Test AUC (Overall)**: **0.74109** (up from 0.678)
- **Thin-File Calibrated Test AUC**: **0.71766** (up from 0.676)
- **Thick-File Calibrated Test AUC**: **0.74353**
- **Deny / Approve Default Rate Ratio**: **6.71x** (Deny actual default rate = 24.41% vs. Approve actual default rate = 3.64%)

---

## Decision Thresholds (Validation-Derived)

- **Approve**: Calibrated Probability $< 0.07643$ (Bottom 60% of distribution · Test Default Rate = 3.64%)
- **Refer for Review**: Calibrated Probability $\in [0.07643, 0.15114]$ (Middle 28% of distribution · Test Default Rate = 10.16%)
- **Deny**: Calibrated Probability $> 0.15114$ (Top 12% of distribution · Test Default Rate = 24.41%)

---

## Fair Lending & Two-Tier Reason Code Governance

- **Two-Tier Architecture**:
  - The model uses all 20 predictive features for credit risk scoring to maximize AUC.
  - The SHAP attribution engine uses `ELIGIBLE_REASON_FEATURES` to strictly gate and filter reason codes so that only the 11 legally authorized statutory factors are ever presented on adverse action notices.
- **Audit Columns (Excluded from Training)**:
  - `CODE_GENDER` (Gender / Sex)
  - `NAME_FAMILY_STATUS` (Marital / Familial status)
  - `age_years` (Age)
- **Dedup Groups**:
  - `loan_size`: `['AMT_CREDIT', 'credit_income_ratio']` (ensures at most one loan size factor is provided in top reasons).
  - `credit_history`: `['bureau_active_credits_count']`.
