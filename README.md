# FairTrace by Synchrony — AI-Powered Credit Risk Assessment & Dual-Lane Regulatory Compliance

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-5.4-646CFF.svg)](https://vitejs.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Problem Statement

Over 45 million Americans and billions globally are classified as "credit invisible" or "thin-file" because they lack conventional credit bureau tradelines. Traditional credit scoring models penalize these individuals automatically, entrenching financial exclusion despite their true creditworthiness.

**FairTrace by Synchrony** bridges this gap using a transparent, compliant, and responsible AI-powered credit risk assessment platform. By combining high-discrimination calibrated Machine Learning (**0.741 AUC**) with a deterministic **Dual-Lane Retrieval-Augmented Generation (RAG)** engine, FairTrace assesses alternative cash flow behavior and traditional credit factors while generating fully explainable, legally grounded Adverse Action Notices under federal consumer financial protection regulations.

---

## Dual-Lane Regulatory Architecture

Under the Equal Credit Opportunity Act (**ECOA / Regulation B, 12 CFR Part 1002**) and the Fair Credit Reporting Act (**FCRA, 15 U.S.C. § 1681m**), creditors cannot rely on vague, generic disclosures or black-box algorithms. FairTrace structures every adverse decision through a **Dual-Lane Compliance Framework**:

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 FAIRTRACE DUAL-LANE COMPLIANCE                                   │
├─────────────────────────────────────────────┬────────────────────────────────────────────────────┤
│   LANE 1: STATUTORY FACTOR AUTHORIZATION    │      LANE 2: PROCEDURAL & AI SPECIFICITY MANDATE   │
├─────────────────────────────────────────────┼────────────────────────────────────────────────────┤
│ • 12 CFR § 1002.6(a), (b)(5), (b)(6)        │ • 12 CFR § 1002.9(b)(2) & Official Commentary      │
│   (Statutory Authority to Evaluate Factors) │   (Mandatory Specific Principal Reasons)           │
│ • Regulation B Appendix C (Form C-1)        │ • CFPB Circulars 2022-03 & 2023-03                 │
│   (Standardized Statutory Reason Checklist) │   (Anti-Vagueness & AI Explainability Standards)   │
│ • Legal Scope & Factor Definitions          │ • FCRA 15 U.S.C. § 1681m Consumer Reporting Notice │
└─────────────────────────────────────────────┴────────────────────────────────────────────────────┘
```

---

## Two-Tier Feature Architecture

FairTrace decouples **predictive accuracy** from **actionable regulatory disclosures**:

1. **Tier 1 — High-AUC Predictive Layer (`ml/model.pkl`)**:
   - Leverages 20 predictive features (including external aggregators `EXT_SOURCE_2/3`, cash flow regularity, and installment velocity) to achieve a **0.741 Test AUC** with **6.71x default separation**.
2. **Tier 2 — Regulatory Reason Whitelist (`backend/inference.py`)**:
   - `ELIGIBLE_REASON_FEATURES` strictly gates the SHAP attribution engine to only emit actionable statutory factors (employment tenure, delinquency share, DTI, installment repayment history). Internal or complex signals are never surfaced to applicants.

---

## End-to-End System Pipeline

```text
  ┌────────────────────────┐
  │  Applicant Data (UI)   │
  └───────────┬────────────┘
              │ HTTP POST /assess (API Key Authentication)
              ▼
  ┌────────────────────────┐
  │   FastAPI Gateway      │
  │   (Pydantic Schema)    │
  └───────────┬────────────┘
              │
              ▼
  ┌────────────────────────────────────────────────────────┐
  │  Two-Tier ML Inference Engine (inference.py)           │
  │  • LightGBM Multi-Feature Prediction (0.741 AUC)       │
  │  • Isotonic Default Probability Calibration            │
  │  • SHAP TreeExplainer & ELIGIBLE_REASON_FEATURES Gate  │
  │  • Decision Engine: Approve (<0.0764) | Deny (>0.1511) │
  └───────────┬────────────────────────────────────────────┘
              │ Top 4 Groundable SHAP Features + Risk Band
              ▼
  ┌────────────────────────────────────────────────────────┐
  │  Dual-Lane Regulatory Retriever (retriever.py)         │
  │  • Deterministic SQLite Exact Lookup by Feature ID     │
  │  • Lane 1 Factor Mapping + Form C-1 Classification     │
  │  • Lane 2 Governance & Specificity Circular Attachment │
  │  • Fallback: all-MiniLM-L6-v2 Semantic Vector Index    │
  └───────────┬────────────────────────────────────────────┘
              │ Grounded Dual-Lane Corpus Context
              ▼
  ┌────────────────────────────────────────────────────────┐
  │  RAG Notice Generator (generator.py)                   │
  │  • Google Gemini 2.5 Flash Lite (temperature=0.0)      │
  │  • AdverseActionNotice Pydantic Model Validation       │
  │  • Deterministic Prohibited Demographic Term Scanner   │
  │  • Citation & Hallucination Guardrails Check           │
  └───────────┬────────────────────────────────────────────┘
              │ Validated JSON Response + Audit Logs
              ▼
  ┌────────────────────────────────────────────────────────┐
  │  React + Vite Frontend (Synchrony Dark Theme)          │
  │  • AssessmentResult & Calibrated Risk Dial             │
  │  • AdverseActionNotice Dual-Lane Document Viewer       │
  │  • Fairness & Segment Disparity Dashboard              │
  │  • Human-in-the-Loop Underwriter Override Panel        │
  └────────────────────────────────────────────────────────┘
```

---

## Setup & Running Locally

### 1. Clone the Repository
```bash
git clone https://github.com/Param-Patel-o5/ai-financial-inclusion-risk-assessment
cd ai-financial-inclusion-risk-assessment
```

### 2. Configure Python Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate environment (Windows PowerShell / CMD):
.venv\Scripts\activate
# On macOS / Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
BACKEND_API_KEY=synchrony-hackathon-2024
```

### 4. Run the Backend Service
```bash
python -m backend.main
```
The FastAPI server will start on `http://localhost:8000` (Swagger docs at `http://localhost:8000/docs`).

### 5. Run the Frontend Application
In a separate terminal:
```bash
cd frontend
npm install
npm run dev
```
The UI is available at `http://localhost:5173`.

### 6. Run the 20-Profile Compliance Evaluation Benchmark
```bash
python -m rag.eval_harness
```

---

## Machine Learning & Model Performance

The LightGBM classifier was trained on 307,511 real-world records with stratified 60/20/20 train/validation/test splits and isotonic probability calibration:

| Metric | Measured Value | Standard / Objective | Status |
| :--- | :---: | :---: | :---: |
| **Overall Calibrated Test AUC** | **0.7411** | High discriminative risk ranking | PASS (✓) |
| **Thin-File Calibrated Test AUC** | **0.7177** | Safe underwriting of unbanked consumers | PASS (✓) |
| **Thick-File Calibrated Test AUC** | **0.7435** | Prime borrower credit risk baseline | PASS (✓) |
| **Default Risk Separation** | **6.71x** | Deny default rate (24.41%) vs. Approve (3.64%) | PASS (✓) |
| **Protected Demographic Bias** | **0.0%** | Gender, family status, age excluded from model | PASS (✓) |

---

## RAG Compliance Evaluation Scorecard (20 Profiles)

Tested against our comprehensive 20-profile benchmark suite (`EVAL_001` through `EVAL_020`) in [`rag/eval_results.json`](file:///c:/Users/Admin/Desktop/Syncrhony%20Assignement/rag/eval_results.json):

| Metric | Target | Benchmark Result | Status |
| :--- | :---: | :---: | :---: |
| **Schema Validity Rate** | 100% | **100.0%** (20/20) | PASS (✓) |
| **Feature Hallucination Rate** | 0% | **0.0%** | PASS (✓) |
| **Citation Hallucination Rate** | 0% | **0.0%** | PASS (✓) |
| **Prohibited Term Violation Rate** | 0% | **0.0%** (0 hits) | PASS (✓) |
| **Mean Retrieval Latency** | < 0.5s | **0.20s** | OPTIMAL |
| **Mean Generation Latency** | < 5.0s | **4.38s** | OPTIMAL |

---

## Decision Thresholds

Derived empirically from validation calibration percentiles:
- **Approve**: Calibrated default probability $< 0.07643$ (Actual test default rate: **3.64%**)
- **Refer**: $0.07643 \le \text{Probability} \le 0.15114$ (Actual test default rate: **10.16%** · Routed to Underwriter Panel)
- **Deny**: Calibrated default probability $> 0.15114$ (Actual test default rate: **24.41%** · Triggers Dual-Lane Notice)

---

## Curated Demo Personas

Pre-configured demo profiles available in the UI for live testing:

| Applicant Name | Persona Archetype | Default Risk | Key Characteristics | Decision |
| :--- | :--- | :---: | :--- | :---: |
| **Maria Santos** | Prime Thick-File | **4.84%** | 8.5 yrs tenure, ₹240k income, 6 bureau lines, 0 late payments | **Approve** |
| **Priya Sharma** | **Thin-File Hero** | **6.80%** | 0 bureau tradelines (`thin_file: 1`), stable 4-yr tenure, low DTI | **Approve** |
| **James Chen** | Borderline Pensioner | **8.94%** | Mixed credit signals, 210 completed installments, pensioner | **Refer** |
| **Marcus Johnson** | High Delinquency | **29.88%** | 44% late payment share, 19 mean days late, 0.32 underpayment | **Deny** |
| **David Vance** | Inquiry Velocity | **35.87%** | 6 recent inquiries, 67% prior refusal rate, short employment | **Deny** |

---

## Tech Stack

| Layer | Technology | Key Capabilities |
| :--- | :--- | :--- |
| **Machine Learning** | LightGBM, SHAP, Isotonic Regression, scikit-learn | Gradient boosting trees, exact SHAP attribution, probability calibration. |
| **RAG & Search** | `sentence-transformers` (`all-MiniLM-L6-v2`), SQLite | Vector embeddings, deterministic statutory indexing, metadata extraction. |
| **LLM & Structuring** | Google Gemini (`gemini-2.5-flash-lite`), Pydantic v2 | Zero-temperature structured generation, adverse notice schema validation. |
| **Backend API** | FastAPI, Uvicorn, Python-dotenv | RESTful endpoints (`/assess`, `/metrics`, `/override`), API key security. |
| **Frontend UI** | React 18, Vite, Recharts, Vanilla CSS | Synchrony yellow/dark palette, responsive layouts, zero-clutter UX. |

---

## Author

**Param Patel**  
B.E. Electronics & Instrumentation, BITS Pilani Hyderabad Campus  
GitHub: [@Param-Patel-o5](https://github.com/Param-Patel-o5)  
Repository: [ai-financial-inclusion-risk-assessment](https://github.com/Param-Patel-o5/ai-financial-inclusion-risk-assessment)
