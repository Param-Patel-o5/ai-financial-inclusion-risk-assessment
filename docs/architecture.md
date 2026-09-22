# FairTrace Architecture & Pipeline Specifications

This document outlines the detailed system architecture and evaluation workflows for the **FairTrace by Synchrony** platform.

---

## 1. End-to-End System Pipeline

The diagram below illustrates the complete end-to-end flow from applicant submission in the React UI through the machine learning and regulatory RAG pipelines to client rendering.

```mermaid
flowchart TD
    subgraph Frontend ["Frontend Layer (React + Vite)"]
        UI["User submits Application Form"]
        AR["AssessmentResult Page"]
        AAN["AdverseActionNotice Page"]
        FD["FairnessDashboard"]
        UP["UnderwriterPanel"]
    end

    subgraph API ["API & Gateway Layer (FastAPI)"]
        POST["POST /assess<br/>(API Key Authentication & Pydantic Validation)"]
        RESP["FastAPI Returns Structured JSON Response"]
    end

    subgraph ML ["Machine Learning Pipeline (inference.py)"]
        LGBM["LightGBM Prediction<br/>(Raw Default Probability)"]
        ISO["Isotonic Calibration<br/>(Calibrated Probability)"]
        SHAP["SHAP TreeExplainer<br/>(Top 4 Key Risk Contributors)"]
        DEC["Decision Band Engine<br/>Approve (< 0.07474) | Deny (> 0.13375) | Refer"]
    end

    subgraph RAG_Retriever ["RAG Regulatory Retriever (retriever.py)"]
        MAP["FEATURE_TO_CLAUSE Deterministic Map"]
        SQL["SQLite Exact Clause Lookup"]
        VEC["Fallback: MiniLM-L6-v2 + ChromaDB Vector Search"]
        RERANK["Relevance Reranker<br/>(Select Top 4 Scored Clauses)"]
    end

    subgraph RAG_Generator ["RAG Notice Generator (generator.py)"]
        ENRICH["Enrich SHAP Features with Pre-bound Clause IDs"]
        PROMPT["Construct Strict Regulatory Prompt"]
        GEMINI["Google Gemini 2.5 Flash Lite<br/>(temperature=0.0)"]
        PYD["Pydantic Output Validation<br/>(AdverseActionNotice Schema)"]
        SCAN["Deterministic Prohibited Term Scan"]
        AUDIT["Citation & Hallucination Audit Flags Check"]
    end

    %% Flow connections
    UI --> POST
    POST --> LGBM
    LGBM --> ISO
    ISO --> SHAP
    SHAP --> DEC
    DEC --> MAP
    MAP --> SQL
    SQL -. Fallback .-> VEC
    SQL --> RERANK
    VEC --> RERANK
    RERANK --> ENRICH
    ENRICH --> PROMPT
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

## 2. Standalone RAG Evaluation Harness Flow

The evaluation harness (`rag/eval_harness.py`) validates the regulatory RAG pipeline in complete isolation using a benchmark of 12 realistic credit profiles across four strict compliance dimensions.

```mermaid
flowchart TD
    subgraph Benchmark ["12 Test Benchmark Profiles"]
        POOL["12 Realistic Profiles<br/>(Thin-File, High-Delinquency, Borderline, Low-Risk)"]
    end

    subgraph Pipeline ["Isolated RAG Execution"]
        RET["retriever.retrieve(shap_features, decision_band, is_thin_file)"]
        GEN["generator.generate(applicant_id, decision_band, prob, is_thin, features, clauses)"]
    end

    subgraph Target_Checks ["4 Target Validation Checks"]
        T1["Target 1: Schema Validity<br/>(Must parse into AdverseActionNotice model)"]
        T2["Target 2: Feature Hallucination<br/>(Every reason feature_name in SHAP inputs)"]
        T3["Target 3: Citation Hallucination<br/>(Every clause_id in retrieved context)"]
        T4["Target 4: Prohibited Term Violations<br/>(Zero protected demographic terms)"]
    end

    subgraph Aggregation ["Reporting & Decision"]
        METRICS["Compute Aggregate Metrics & Generation Latencies"]
        RESULT{"Pass / Fail per Target"}
        REPORT["Generate Terminal Table & Log Report"]
    end

    %% Flow connections
    POOL --> RET
    RET --> GEN
    GEN --> T1
    GEN --> T2
    GEN --> T3
    GEN --> T4
    T1 --> METRICS
    T2 --> METRICS
    T3 --> METRICS
    T4 --> METRICS
    METRICS --> RESULT
    RESULT --> REPORT
```
