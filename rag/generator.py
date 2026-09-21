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
1. Every reason you state must correspond EXACTLY to one feature in SHAP_REASONS. Do not invent or add reasons.
2. Every citation must appear EXACTLY in RETRIEVED_CLAUSES. Do not cite anything outside that list.
3. Do not use these prohibited terms or synonyms: race, color, religion, national origin, sex, marital status, age, familial status, disability, public assistance, gender.
4. Write plain English at 8th-grade reading level.
5. Do not state or imply a final credit decision. State reasons only.
6. Output ONLY valid JSON matching the schema below. No preamble, no markdown, no explanation.

OUTPUT SCHEMA:
{{
  "applicant_id": "<string>",
  "decision_band": "<Approve|Refer|Deny>",
  "calibrated_probability": <float>,
  "reasons": [
    {{
      "rank": <1|2|3|4>,
      "feature_name": "<exact feature name from SHAP_REASONS>",
      "plain_english_reason": "<one sentence, max 25 words>",
      "regulatory_basis": {{
        "clause_id": "<exact chunk_id from RETRIEVED_CLAUSES>",
        "citation": "<exact citation string from RETRIEVED_CLAUSES>",
        "requirement": "<one sentence: what this regulation requires>"
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

SHAP_REASONS (only these features may appear in your output):
{shap_reasons_block}

RETRIEVED_CLAUSES (only these citations may appear in your output):
{retrieved_clauses_block}

Write the Adverse Action Notice JSON now."""


# ─── HELPERS ──────────────────────────────────────────

def build_shap_block(shap_features: list[dict]) -> str:
    lines = []

    for i, f in enumerate(shap_features, 1):
        lines.append(
            f"{i}. Feature: {f['feature_name']}\n"
            f"   Value: {f['value']}\n"
            f"   SHAP Impact: {f['shap']} (positive = increases default risk)"
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
        {
            "feature_name": "late_payment_share",
            "value": 0.35,
            "shap": 0.142
        },
        ...
    ]

    retrieved_clauses:
    output from retriever.retrieve()["retrieved_clauses"]

    Returns:
    {
        "notice": AdverseActionNotice dict,
        "audit_flags": list of any pre/post violations found
    }
    """

    audit_flags = []


    # ── PRE-CHECK 1: enough clauses retrieved ─────────

    if len(retrieved_clauses) < 2:
        audit_flags.append(
            "RETRIEVAL_INSUFFICIENT: fewer than 2 clauses"
        )


    # ── PRE-CHECK 2: prohibited terms in feature names ─

    for f in shap_features:

        hits = check_prohibited_terms(
            f["feature_name"]
        )

        if hits:
            audit_flags.append(
                f"PROHIBITED_FEATURE: "
                f"{f['feature_name']} contains {hits}"
            )


    # ── BUILD PROMPT ──────────────────────────────────

    prompt = GENERATION_PROMPT.format(
        applicant_id=applicant_id,
        decision_band=decision_band,
        calibrated_prob=calibrated_prob,
        is_thin_file=is_thin_file,
        shap_reasons_block=build_shap_block(shap_features),
        retrieved_clauses_block=build_clauses_block(
            retrieved_clauses
        )
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

    valid_features = {
        f["feature_name"]
        for f in shap_features
    }

    for reason in notice_dict.get("reasons", []):

        if reason["feature_name"] not in valid_features:

            audit_flags.append(
                f"HALLUCINATED_FEATURE: "
                f"{reason['feature_name']} "
                f"not in SHAP output"
            )


    # ── POST-CHECK 2: citations not hallucinated ──────

    valid_chunk_ids = {
        c["chunk_id"]
        for c in retrieved_clauses
    }

    for reason in notice_dict.get("reasons", []):

        cid = reason["regulatory_basis"]["clause_id"]

        if cid not in valid_chunk_ids:

            audit_flags.append(
                f"HALLUCINATED_CITATION: "
                f"{cid} not in retrieved clauses"
            )


    # ── POST-CHECK 3: prohibited terms in output ──────

    disclosure = notice_dict.get(
        "disclosure_statement",
        ""
    )

    hits = check_prohibited_terms(disclosure)

    if hits:

        audit_flags.append(
            f"PROHIBITED_BASIS_IN_OUTPUT: {hits}"
        )


    # ── VALIDATE SCHEMA ───────────────────────────────

    notice = AdverseActionNotice(
        **notice_dict
    )


    # ── RETURN ────────────────────────────────────────

    return {
        "notice": notice.model_dump(),
        "audit_flags": audit_flags
    }


# ─── QUICK TEST ───────────────────────────────────────

if __name__ == "__main__":

    from retriever import retrieve


    retriever_output = retrieve(

        shap_features=[
            {
                "feature_name": "late_payment_share",
                "value": 0.35,
                "shap": 0.142
            },
            {
                "feature_name": "prev_refusal_rate",
                "value": 0.82,
                "shap": 0.118
            },
            {
                "feature_name": "mean_days_late",
                "value": 12.0,
                "shap": 0.095
            }
        ],

        decision_band="Deny",

        is_thin_file=True,

        applicant_id="TEST_001"
    )


    result = generate(

        applicant_id="TEST_001",

        decision_band="Deny",

        calibrated_prob=0.18,

        is_thin_file=True,

        shap_features=[
            {
                "feature_name": "late_payment_share",
                "value": 0.35,
                "shap": 0.142
            },
            {
                "feature_name": "prev_refusal_rate",
                "value": 0.82,
                "shap": 0.118
            },
            {
                "feature_name": "mean_days_late",
                "value": 12.0,
                "shap": 0.095
            }
        ],

        retrieved_clauses=retriever_output[
            "retrieved_clauses"
        ]
    )


    print(
        json.dumps(
            result,
            indent=2
        )
    )