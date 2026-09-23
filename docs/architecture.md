# FairTrace Architecture & System Specifications

This document details the system design, two-tier machine learning pipeline, and Dual-Lane regulatory RAG architecture of **FairTrace by Synchrony**.

---

## 1. End-to-End System Architecture

```mermaid
flowchart TD
    subgraph Frontend ["Frontend Layer (React 19 + Vite 8)"]
        UI["User submits Application Form"]
        AR["AssessmentResult Page"]
        AAN["AdverseActionNotice Page (Dual-Lane View)"]
        FD["FairnessDashboard (0.741 AUC Benchmark)"]
        UP["UnderwriterPanel (Audit Logging)"]
    end

    subgraph API ["API & Gateway Layer (FastAPI)"]
        POST["POST /assess<br/>(API Key Authentication & Pydantic Validation)"]
        RESP["FastAPI Returns Structured JSON Response"]
    end

    subgraph ML ["Two-Tier ML Pipeline (inference.py)"]
        LGBM["LightGBM Prediction on 20 Features<br/>(Test AUC: 0.7411)"]
        ISO["Isotonic Probability Calibration<br/>(Floor: 0.005)"]
        SHAP["SHAP TreeExplainer Attribution"]
        GATE{"ELIGIBLE_REASON_FEATURES<br/>Statutory Whitelist Gate"}
        DEC["Decision Engine<br/>Approve (< 0.0764) | Deny (> 0.1511) | Refer"]
    end

    subgraph RAG_Retriever ["Dual-Lane Regulatory Retriever (retriever.py)"]
        SQL["Deterministic SQLite Clause Index"]
        L1["Lane 1: 12 CFR § 1002.6 & Form C-1 Authority"]
        L2["Lane 2: CFPB Circulars 2022-03 / 2023-03 & FCRA § 1681m"]
        VEC["Semantic Vector Fallback (all-MiniLM-L6-v2)"]
    end

    subgraph RAG_Generator ["RAG Notice Generator (generator.py)"]
        PROMPT["Structured Regulatory Prompting"]
        GEMINI["Google Gemini 2.5 Flash Lite<br/>(temperature=0.0)"]
        PYD["Pydantic Output Validation<br/>(AdverseActionNotice Model)"]
        SCAN["Deterministic Prohibited Demographic Term Scanner"]
        AUDIT["Citation & Hallucination Audit Flags Check"]
    end

    %% Flow connections
    UI --> POST
    POST --> LGBM
    LGBM --> ISO
    ISO --> SHAP
    SHAP --> GATE
    GATE --> DEC
    DEC --> SQL
    SQL --> L1
    SQL --> L2
    SQL -. Fallback .-> VEC
    L1 --> PROMPT
    L2 --> PROMPT
    PROMPT --> GEMINI
    GEMINI --> PYD
    PYD --> SCAN
    SCAN --> AUDIT
    AUDIT --> RESP
    RESP --> AR
    RESP --> AAN
    RESP --> FD
    RESP --> UP
```

---

## 2. Dual-Lane Compliance Model

FairTrace solves the regulatory challenge of black-box AI by enforcing a two-lane statutory structure on every generated adverse action reason code:

### Lane 1: Substantive Factor Authorization
- **Statutory Authority**: **12 CFR § 1002.6(a), (b)(5), and (b)(6)**.
- **Form C-1 Checklist Alignment**: Regulation B Appendix C Sample Form C-1 line items (e.g., `Part I (Item 15): Delinquent past or present credit obligations with others`).
- **Legal Scope**: Explicit statutory boundary describing the creditor's legal authority to evaluate the specific risk factor.

### Lane 2: Procedural Specificity & AI Governance Mandate
- **Governing Directives**:
  - **12 CFR § 1002.9(b)(2)** & Official Staff Commentary: Requirement to state specific, principal reasons.
  - **CFPB Circular 2022-03**: Black-box algorithmic complexity does not exempt creditors from providing actionable, specific reasons.
  - **CFPB Circular 2023-03**: Prohibition against relying on generic checklist items when complex ML models score non-traditional factors.
  - **FCRA 15 U.S.C. § 1681m**: Consumer reporting agency disclosures and credit dispute rights.

---

## 3. Two-Tier Machine Learning Pipeline

```mermaid
flowchart LR
    subgraph Data ["Feature Ingestion"]
        APP["Application Data<br/>(Income, Credit, Tenure)"]
        ALT["Alternative Data<br/>(Cash Flow, Installments)"]
        EXT["Internal Aggregators<br/>(EXT_SOURCE_2/3, Inquiries)"]
    end

    subgraph Tier1 ["Tier 1: High-AUC Model"]
        ALL_FEATS["20 Ingested Features"]
        LGBM_MODEL["Calibrated LightGBM Classifier<br/>(0.741 Test AUC)"]
        RISK_SCORE["Calibrated Default Probability"]
    end

    subgraph Tier2 ["Tier 2: Explainable Reason Whitelist"]
        SHAP_EXP["TreeSHAP Attribution"]
        FILTER{"ELIGIBLE_REASON_FEATURES<br/>Whitelist Filter"}
        SAFE_FEATS["Top Actionable Statutory Factors<br/>(Debt Burden, Delinquency, Tenure)"]
    end

    APP --> ALL_FEATS
    ALT --> ALL_FEATS
    EXT --> ALL_FEATS
    ALL_FEATS --> LGBM_MODEL
    LGBM_MODEL --> RISK_SCORE
    LGBM_MODEL --> SHAP_EXP
    SHAP_EXP --> FILTER
    FILTER --> SAFE_FEATS
```

---

## 4. Empirical Benchmark Validation (20 Test Profiles)

Across our 20-profile benchmark harness (`rag/eval_harness.py`):
- **Schema Validity**: 100.0% (20/20 Pydantic AdverseActionNotice instances validated)
- **Feature Hallucination Rate**: 0.0% (Zero ungrounded factors emitted)
- **Citation Hallucination Rate**: 0.0% (100% verified against SQLite regulatory index)
- **Prohibited Demographic Term Leakage**: 0.0% (0 ECOA violations)
- **Mean Retrieval Latency**: 0.20 seconds
- **Mean Generation Latency**: 4.38 seconds
