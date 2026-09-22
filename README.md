# FairTrace by Synchrony — AI-Powered Credit Risk Assessment

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-5.4-646CFF.svg)](https://vitejs.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Problem Statement

Over 45 million Americans and billions globally are classified as "credit invisible" or "thin-file" because they lack conventional credit bureau tradelines. Traditional credit scoring models penalize these individuals automatically, entrenching financial exclusion despite their true creditworthiness. **FairTrace by Synchrony** bridges this gap using a transparent, compliant, and responsible AI-powered credit risk assessment platform. By combining calibrated Machine Learning with deterministic and grounded Retrieval-Augmented Generation (RAG), FairTrace assesses both alternative cash flow behavior and traditional credit factors while generating fully explainable, legally binding Adverse Action Notices that comply with federal consumer financial protection laws.

---

## Architecture Overview

```text
  ┌───────────────────────┐
  │  Applicant Data (UI)  │
  └──────────┬────────────┘
             │ HTTP POST /assess (API Key Auth)
             ▼
  ┌───────────────────────┐
  │  FastAPI Backend      │
  │  (Schema Validation)  │
  └──────────┬────────────┘
             │
             ▼
  ┌────────────────────────────────────────────────────────┐
  │  ML Inference Pipeline (inference.py)                  │
  │  • LightGBM Model Prediction                           │
  │  • Isotonic Probability Calibration                    │
  │  • SHAP TreeExplainer (Top 4 Risk Contributors)        │
  │  • Decision Engine: Approve (<0.07474) | Deny (>0.13375│
  └──────────┬─────────────────────────────────────────────┘
             │ Top 4 SHAP Features + Decision Band
             ▼
  ┌────────────────────────────────────────────────────────┐
  │  RAG Regulatory Retriever (retriever.py)               │
  │  • FEATURE_TO_CLAUSE Deterministic SQLite Lookup       │
  │  • Fallback: all-MiniLM-L6-v2 Embeddings + ChromaDB    │
  │  • Cross-Encoder / Relevance Reranker (Top 4 Clauses)  │
  └──────────┬─────────────────────────────────────────────┘
             │ Enriched Features & Regulatory Clauses
             ▼
  ┌────────────────────────────────────────────────────────┐
  │  RAG Notice Generator (generator.py)                   │
  │  • Google Gemini 2.5 Flash Lite (temperature=0.0)      │
  │  • Pydantic Schema Parsing (AdverseActionNotice)       │
  │  • Deterministic Prohibited Term Scanner               │
  │  • Citation & Hallucination Guardrails                 │
  └──────────┬─────────────────────────────────────────────┘
             │ Validated JSON Response + Audit Flags
             ▼
  ┌────────────────────────────────────────────────────────┐
  │  React + Vite Frontend (Synchrony Theme)               │
  │  • AssessmentResult & Risk Breakdown                   │
  │  • AdverseActionNotice Viewer                          │
  │  • Fairness & Segment Disparity Dashboard              │
  │  • Human-in-the-Loop Underwriter Panel                 │
  └────────────────────────────────────────────────────────┘
```

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Param-Patel-o5/ai-financial-inclusion-risk-assessment
cd ai-financial-inclusion-risk-assessment
```

### 2. Configure Python Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate environment
# On Windows (PowerShell / CMD):
.venv\Scripts\activate
# On macOS / Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_key_here
API_KEY=your_fastapi_key_here
```

### 4. Run the Backend Service
```bash
python -m backend.main
```
The FastAPI server will start on `http://localhost:8000` with Swagger docs available at `http://localhost:8000/docs`.

### 5. Run the Frontend Application
Open a separate terminal:
```bash
cd frontend
npm install
npm run dev
```
The UI will be accessible at `http://localhost:5173`.

### 6. Run the RAG Evaluation Harness
```bash
python -m rag.eval_harness
```

---

## Tech Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Machine Learning** | LightGBM, SHAP, Isotonic Regression, scikit-learn | Gradient boosting risk classification, exact feature attribution, calibrated default probabilities. |
| **RAG & Search** | `sentence-transformers` (`all-MiniLM-L6-v2`), ChromaDB, SQLite | Semantic embeddings, regulatory clause vector storage, deterministic legal indexing. |
| **LLM & Generation** | Google Gemini (`gemini-2.5-flash-lite`), Pydantic v2 | Zero-temperature legally structured adverse action generation and JSON schema enforcement. |
| **Backend API** | FastAPI, Uvicorn, Pydantic, python-dotenv | Asynchronous REST API, API key authentication, request/response validation, audit logging. |
| **Frontend UI** | React 18, Vite, Recharts, React Router DOM | Responsive Synchrony yellow/black branded UI, interactive charts, real-time status monitoring. |
| **Testing & Evaluation** | Custom Eval Harness, Pytest | Standalone RAG evaluation against 4 strict compliance targets across 12 realistic test profiles. |

---

## Regulatory Compliance

FairTrace is engineered specifically to adhere to federal consumer financial protection and anti-discrimination mandates:

- **ECOA / Regulation B (12 CFR § 1002.9)**: Governs adverse action notices, mandating specific, non-vague reasons for credit denial and strictly prohibiting discrimination on protected demographic grounds.
- **FCRA (15 U.S.C. § 1681m)**: Governs consumer credit reporting disclosures, requiring clear explanations when credit bureau or alternative data affects loan terms or decisions.
- **CFPB Circular 2022-03**: Mandates explainability when utilizing complex or alternative data sources, prohibiting black-box exclusions of underserved consumers.
- **CFPB Circular 2023-03**: Requires strict specificity and technical accuracy in adverse action reasons when AI/ML algorithms are used in credit decisions.

---

## RAG Evaluation Metrics

Evaluated across a benchmark of 20 diverse test profiles (including thin-file, high-delinquency, and borderline applicants):

| Metric Target | Measured Value | Standard / Requirement | Status |
| :--- | :---: | :---: | :---: |
| **Schema Validity Rate** | **100.0%** | Must parse cleanly into `AdverseActionNotice` Pydantic model | PASS |
| **Feature Hallucination Rate** | **0.0%** | Generated reasons must strictly originate from top SHAP features | PASS |
| **Citation Hallucination Rate** | **0.0%** | Every cited legal clause must exist in retrieved regulatory corpus | PASS |
| **Prohibited Term Violation Rate**| **0.0%** | Zero prohibited demographic or protected-class terminology | PASS |
| **Mean Retrieval Latency** | **0.17s** | Sub-second SQLite vector / exact retrieval | PASS |
| **Mean Generation Latency** | **3.00s** | Real-time SLA for interactive underwriting workflows | PASS |

---

## Decision Thresholds

- **Approve**: Calibrated default probability $< 0.07474$
- **Deny**: Calibrated default probability $> 0.13375$
- **Refer**: $0.07474 \le \text{Probability} \le 0.13375$ (Routed to Human-in-the-Loop Underwriter Panel)

---

## Demo Profiles

Pre-configured demo profiles available in the UI for instant testing:

| Profile Name | Profile Archetype | Key Characteristics | Expected Decision |
| :--- | :--- | :--- | :---: |
| **Priya Sharma** | Thin-File Deny | 0 bureau tradelines, high credit-to-income ratio (6.12), low tenure | **Deny** |
| **Marcus Johnson** | Thick-File Deny | High late payment share (44%), 19 days mean late, prior refusals | **Deny** |
| **James Chen** | Borderline Refer | Mixed history, 7 active bureau credits, 10.9% late payment share | **Refer** |
| **Aisha Patel** | Thin-File Refer | 0 bureau tradelines, low debt ratio (2.50), pristine alternative history | **Refer** |
| **Maria Santos** | Strong Profile | Stable employment, 0 late payments, low debt burden | **Approve** |

---

## Engineering Practices

- **API-First Architecture**: Clean separation between FastAPI backend services, inference engine, RAG pipeline, and React frontend.
- **Zero Hardcoded Secrets**: Complete configuration via `.env` files with environment variable fallbacks and `.gitignore` hygiene.
- **Pydantic Schema Validation**: End-to-end type safety and JSON schema validation for all API inputs, ML payloads, and LLM structured outputs.
- **Deterministic Guardrails**: Multi-tier prohibited term scanning and regulatory cross-referencing that guarantee zero hallucinated legal citations.
- **4-Target Standalone Evaluation Harness**: Independent test suite benchmarking schema validity, feature faithfulness, citation integrity, and safety.
- **Human-in-the-Loop Governance**: Dedicated Underwriter Panel with comprehensive audit logging for borderline decisions and manual overrides.

---

## Author

**Param Patel**  
B.E. Electronics & Instrumentation, BITS Pilani Hyderabad Campus  
GitHub: [@Param-Patel-o5](https://github.com/Param-Patel-o5)  
Repository: [ai-financial-inclusion-risk-assessment](https://github.com/Param-Patel-o5/ai-financial-inclusion-risk-assessment)
