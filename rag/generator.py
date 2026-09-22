# rag/generator.py

import json
import re
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

import google.generativeai as genai


# ─── CONFIG ───────────────────────────────────────────

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

MODEL = "gemini-3.5-flash-lite"


# ─── FEATURE → CLAUSE MAP (single source of truth) ────

FEATURE_TO_CLAUSE = {
    "employment_years":     "regb_1002_9_b_2",
    "thin_file":            "circular_2022_03_analysis_p1",
    "installments_count":   "circular_2023_03_analysis_p3",
    "annuity_income_ratio": "regb_1002_9_b_2",
    "late_payment_share":   "regb_1002_9_b_2",
    "prev_refusal_rate":    "fcra_1681m_a",
    "credit_income_ratio":  "regb_1002_9_b_2",
}


# ─── OUTPUT SCHEMA (Pydantic) ─────────────────────────

class RegulatoryBasis(BaseModel):
    clause_id: str
    citation: str
    requirement: str


class ReasonCode(BaseModel):
    rank: int
    feature_name: str
    plain_english_reason: str
    regulatory_basis: RegulatoryBasis


class AdverseActionNotice(BaseModel):
    applicant_id: str
    decision_band: str
    calibrated_probability: float
    reasons: list[ReasonCode]
    disclosure_statement: str


# ─── PROHIBITED TERMS (deterministic pre-check) ───────

PROHIBITED_TERMS = [
    "race",
    "color",
    "religion",
    "national origin",
    "sex",
    "marital status",
    "age",
    "familial status",
    "disability",
    "public assistance",
    "gender",
]


# ─── PROMPT TEMPLATE ──────────────────────────────────

GENERATION_PROMPT = """You are a compliance officer writing an Adverse Action Notice under ECOA (Regulation B) and FCRA.
Your output will be reviewed by a federal regulator.

RULES — follow without exception:
The plain_english_reason must reflect the direction of the SHAP Impact. 
A positive SHAP value means this feature increases default risk — phrase 
the reason accordingly (e.g. "too many", "too high", "too short"). 
Never invert the direction.
2. Each reason has a PRE-ASSIGNED clause in SHAP_REASONS marked as ASSIGNED_CLAUSE_ID. You MUST use that exact clause_id for that reason. Do not swap clauses between reasons under any circumstance.
3. Do not use these prohibited terms or synonyms: race, color, religion, national origin, sex, marital status, age, familial status, disability, public assistance, gender.
4. Write plain English at 8th-grade reading level.
5. Do not state or imply a final credit decision. State reasons only. Do not use phrases like "areas for improvement", "key areas", "next steps", or any language implying the applicant caused or can fix the decision. The disclosure_statement must only state that specific reasons are provided as required by law and that the applicant has the right to request the information used.
6. For the requirement field: copy the most relevant sentence directly from the 
CLAUSE_TEXT provided for that feature in SHAP_REASONS. Do not paraphrase or 
rewrite it. If CLAUSE_TEXT has multiple sentences, pick the one most directly 
governing that specific credit factor.7. Output ONLY valid JSON matching the schema below. No preamble, no markdown, no explanation.

OUTPUT SCHEMA:
{{
  "applicant_id": "<string>",
  "decision_band": "<Approve|Refer|Deny>",
  "calibrated_probability": <float>,
  "reasons": [
    {{
      "rank": <1|2|3|4>,
      "feature_name": "<exact feature_name from SHAP_REASONS>",
      "plain_english_reason": "<one sentence, max 25 words>",
      "regulatory_basis": {{
        "clause_id": "<ASSIGNED_CLAUSE_ID for this feature — copy exactly>",
        "citation": "<exact citation string for that clause_id from RETRIEVED_CLAUSES>",
        "requirement": "<one sentence per Rule 6 above>"
      }}
    }}
  ],
  "disclosure_statement": "<2-3 sentence plain English summary suitable for mailing to applicant>"
}}

---

APPLICANT_ID: {applicant_id}
DECISION_BAND: {decision_band}
CALIBRATED_PROBABILITY: {calibrated_prob}
THIN_FILE: {is_thin_file}

SHAP_REASONS (each feature has a pre-assigned clause — copy ASSIGNED_CLAUSE_ID exactly, no reassignment):
{shap_reasons_block}

RETRIEVED_CLAUSES (use only to look up citation text and requirement text for the ASSIGNED_CLAUSE_ID — do not reassign):
{retrieved_clauses_block}

Write the Adverse Action Notice JSON now."""


# ─── HELPERS ──────────────────────────────────────────

def enrich_shap_with_clauses(
    shap_features: list[dict],
    retrieved_clauses: list[dict]
) -> list[dict]:
    """
    Injects clause_id into each shap feature using FEATURE_TO_CLAUSE map.
    Falls back to first retrieved clause if feature not in map or clause
    not in retrieved set.
    """
    clause_ids_retrieved = {c["chunk_id"] for c in retrieved_clauses}
    fallback = retrieved_clauses[0]["chunk_id"]

    enriched = []
    for f in shap_features:
        clause_id = FEATURE_TO_CLAUSE.get(f["feature_name"])

        if not clause_id or clause_id not in clause_ids_retrieved:
            clause_id = fallback

        enriched.append({**f, "clause_id": clause_id})

    return enriched

def build_shap_block(shap_features: list[dict], retrieved_clauses: list[dict]) -> str:
    """
    Now takes retrieved_clauses too, so it can embed actual clause text per feature.
    """
    clause_lookup = {c["chunk_id"]: c for c in retrieved_clauses}
    lines = []
    for i, f in enumerate(shap_features, 1):
        clause = clause_lookup.get(f["clause_id"], {})
        clause_text = clause.get("text", "")[:300]  # cap at 300 chars to save tokens
        lines.append(
            f"{i}. Feature: {f['feature_name']}\n"
            f"   Value: {f['value']}\n"
            f"   SHAP Impact: {f['shap']} (positive = increases default risk)\n"
            f"   ASSIGNED_CLAUSE_ID: {f['clause_id']}  ← use this clause_id for this reason, no other\n"
            f"   CLAUSE_TEXT: \"{clause_text}\""
        )
    return "\n\n".join(lines)


def build_clauses_block(retrieved_clauses: list[dict]) -> str:
    lines = []
    for i, c in enumerate(retrieved_clauses, 1):
        lines.append(
            f"[CLAUSE {i}]\n"
            f"chunk_id: {c['chunk_id']}\n"
            f"citation: {c['citation']}\n"
            f"text: {c['text']}"
        )
    return "\n\n".join(lines)


def check_prohibited_terms(text: str) -> list[str]:
    """Deterministic scan — runs before LLM and after."""
    found = []
    lower = text.lower()
    for term in PROHIBITED_TERMS:
        if term in lower:
            found.append(term)
    return found


def parse_llm_json(raw: str) -> dict:
    """Strip markdown fences if LLM adds them despite instructions."""
    cleaned = re.sub(r"```json|```", "", raw).strip()
    return json.loads(cleaned)


# ─── MAIN GENERATE FUNCTION ───────────────────────────

def generate(
    applicant_id: str,
    decision_band: str,
    calibrated_prob: float,
    is_thin_file: bool,
    shap_features: list[dict],
    retrieved_clauses: list[dict]
) -> dict:

    """
    shap_features format:
    [
        {"feature_name": "late_payment_share", "value": 0.35, "shap": 0.142},
        ...
    ]
    clause_id is injected automatically — do not pass it manually.

    retrieved_clauses: output from retriever.retrieve()["retrieved_clauses"]

    Returns:
    {
        "notice": AdverseActionNotice dict,
        "audit_flags": list of any pre/post violations found
    }
    """

    audit_flags = []

    # ── PRE-CHECK 1: enough clauses retrieved ─────────
    if len(retrieved_clauses) < 2:
        audit_flags.append("RETRIEVAL_INSUFFICIENT: fewer than 2 clauses")

        # ── PRE-CHECK 2: prohibited terms in feature names ─
    for f in shap_features:
        hits = check_prohibited_terms(f["feature_name"])
        if hits:
            audit_flags.append(
                f"PROHIBITED_FEATURE: {f['feature_name']} contains {hits}"
            )

    # ── ENRICH SHAP WITH CLAUSE BINDINGS ──────────────
    enriched_shap = enrich_shap_with_clauses(shap_features, retrieved_clauses)

    # ── BUILD PROMPT ──────────────────────────────────
    prompt = GENERATION_PROMPT.format(
        applicant_id=applicant_id,
        decision_band=decision_band,
        calibrated_prob=calibrated_prob,
        is_thin_file=is_thin_file,
        shap_reasons_block=build_shap_block(enriched_shap, retrieved_clauses),  # ← updated signature
        retrieved_clauses_block=build_clauses_block(retrieved_clauses)
    )

    # ── LLM CALL ──────────────────────────────────────
    model = genai.GenerativeModel(
        model_name=MODEL,
        generation_config=genai.types.GenerationConfig(
            temperature=0.0,
            max_output_tokens=2000,
            response_mime_type="application/json"
        )
    )

    response = model.generate_content(prompt)

    # ── GET RAW OUTPUT ─────────────────────────────────
    raw_output = response.text

    # ── PARSE ─────────────────────────────────────────
    notice_dict = parse_llm_json(raw_output)

    # ── POST-CHECK 1: feature names not hallucinated ──
    valid_features = {f["feature_name"] for f in shap_features}
    for reason in notice_dict.get("reasons", []):
        if reason["feature_name"] not in valid_features:
            audit_flags.append(
                f"HALLUCINATED_FEATURE: {reason['feature_name']} not in SHAP output"
            )

    # ── POST-CHECK 2: citations not hallucinated ──────
    valid_chunk_ids = {c["chunk_id"] for c in retrieved_clauses}
    for reason in notice_dict.get("reasons", []):
        cid = reason["regulatory_basis"]["clause_id"]
        if cid not in valid_chunk_ids:
            audit_flags.append(
                f"HALLUCINATED_CITATION: {cid} not in retrieved clauses"
            )

    # ── POST-CHECK 3: prohibited terms in output ──────
    disclosure = notice_dict.get("disclosure_statement", "")
    hits = check_prohibited_terms(disclosure)
    if hits:
        audit_flags.append(f"PROHIBITED_BASIS_IN_OUTPUT: {hits}")

    # ── POST-CHECK 4: clause binding respected ─────────
    feature_to_assigned = {f["feature_name"]: f["clause_id"] for f in enriched_shap}
    for reason in notice_dict.get("reasons", []):
        fname = reason["feature_name"]
        returned_cid = reason["regulatory_basis"]["clause_id"]
        expected_cid = feature_to_assigned.get(fname)
        if expected_cid and returned_cid != expected_cid:
            audit_flags.append(
                f"CLAUSE_MISMATCH: {fname} expected {expected_cid} "
                f"but Gemini returned {returned_cid}"
            )

    # ── VALIDATE SCHEMA ───────────────────────────────
    notice = AdverseActionNotice(**notice_dict)

    # ── RETURN ────────────────────────────────────────
    return {
        "notice": notice.model_dump(),
        "audit_flags": audit_flags
    }


# ─── QUICK TEST ───────────────────────────────────────

if __name__ == "__main__":

    from retriever import retrieve

    test_shap = [
        {"feature_name": "thin_file",         "value": 1,    "shap": 0.31},
        {"feature_name": "employment_years",  "value": 0.5,  "shap": 0.18},
        {"feature_name": "installments_count","value": 8,    "shap": 0.14},
        {"feature_name": "annuity_income_ratio","value": 0.6,"shap": 0.11},
    ]

    retriever_output = retrieve(
        shap_features=test_shap,
        decision_band="Deny",
        is_thin_file=True,
        applicant_id="TEST_001"
    )

    result = generate(
        applicant_id="TEST_001",
        decision_band="Deny",
        calibrated_prob=0.18,
        is_thin_file=True,
        shap_features=test_shap,
        retrieved_clauses=retriever_output["retrieved_clauses"]
    )

    print(json.dumps(result, indent=2))