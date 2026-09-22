# rag/generator.py

import json
import re
import os
import sys
from pydantic import BaseModel
from dotenv import load_dotenv

# Configure UTF-8 output encoding for Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()

import google.generativeai as genai


# ─── CONFIG ───────────────────────────────────────────

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")


# ─── FEATURE METADATA MAP (14 TARGET CHUNKS) ──────────

FEATURE_METADATA = {
    # Payment History
    "late_payment_share": {
        "standard_category": "Delinquent past or present credit obligations with others",
        "form_c1_item": "Part I (Item 15): Delinquent past or present credit obligations with others",
        "statutory_scope": "Authorizes evaluation of delinquency frequency, late payment share, and historical installment repayment records.",
        "lane_1_id": "regb_1002_6_b_6",
        "lane_2_id": "interp_9_b2_comment4",
    },
    "mean_days_late": {
        "standard_category": "Delinquent past or present credit obligations with others",
        "form_c1_item": "Part I (Item 15): Delinquent past or present credit obligations with others",
        "statutory_scope": "Authorizes evaluation of average delinquency duration and timeliness of previous payments.",
        "lane_1_id": "regb_1002_6_b_6",
        "lane_2_id": "interp_9_b2_comment4",
    },
    "max_days_late": {
        "standard_category": "Delinquent past or present credit obligations with others",
        "form_c1_item": "Part I (Item 15): Delinquent past or present credit obligations with others",
        "statutory_scope": "Authorizes evaluation of maximum days past due and severe delinquency events.",
        "lane_1_id": "regb_1002_6_b_6",
        "lane_2_id": "interp_9_b2_comment4",
    },
    "underpayment_share": {
        "standard_category": "Delinquent past or present credit obligations with others",
        "form_c1_item": "Part I (Item 15): Delinquent past or present credit obligations with others",
        "statutory_scope": "Authorizes consideration of partial payments, payment amounts, and installment shortfall records.",
        "lane_1_id": "regb_1002_6_b_6",
        "lane_2_id": "interp_9_b2_comment4",
    },

    # Income & Debt Ratios
    "credit_income_ratio": {
        "standard_category": "Income insufficient for amount of credit requested",
        "form_c1_item": "Part I (Item 8): Income insufficient for amount of credit requested",
        "statutory_scope": "Authorizes consideration of requested loan size relative to income amount and debt service capacity.",
        "lane_1_id": "regb_1002_6_b_5",
        "lane_2_id": "regb_1002_9_b_2",
    },
    "annuity_income_ratio": {
        "standard_category": "Excessive obligations in relation to income",
        "form_c1_item": "Part I (Item 9): Excessive obligations in relation to income",
        "statutory_scope": "Authorizes evaluation of recurring debt burden and annuity continuity relative to total income.",
        "lane_1_id": "regb_1002_6_b_5",
        "lane_2_id": "regb_1002_9_b_2",
    },
    "AMT_CREDIT": {
        "standard_category": "Income insufficient for amount of credit requested",
        "form_c1_item": "Part I (Item 8): Income insufficient for amount of credit requested",
        "statutory_scope": "Authorizes evaluation of total credit requested against applicant earnings and repayment ability.",
        "lane_1_id": "regb_1002_6_b_5",
        "lane_2_id": "regb_1002_9_b_2",
    },
    "AMT_INCOME_TOTAL": {
        "standard_category": "Income insufficient for amount of credit requested",
        "form_c1_item": "Part I (Item 8): Income insufficient for amount of credit requested",
        "statutory_scope": "Authorizes evaluation of total verified income amount and probable continuance.",
        "lane_1_id": "regb_1002_6_b_5",
        "lane_2_id": "regb_1002_9_b_2",
    },
    "AMT_ANNUITY": {
        "standard_category": "Excessive obligations in relation to income",
        "form_c1_item": "Part I (Item 9): Excessive obligations in relation to income",
        "statutory_scope": "Authorizes evaluation of annual payment obligations relative to income flow.",
        "lane_1_id": "regb_1002_6_b_5",
        "lane_2_id": "regb_1002_9_b_2",
    },

    # Employment & Demographics
    "employment_years": {
        "standard_category": "Length of employment",
        "form_c1_item": "Part I (Item 7): Length of employment",
        "statutory_scope": "Authorizes evaluation of employment duration, tenure stability, and job continuity.",
        "lane_1_id": "regb_1002_6_a",
        "lane_2_id": "interp_9_b2_comment2",
    },
    "NAME_INCOME_TYPE": {
        "standard_category": "Temporary or irregular employment",
        "form_c1_item": "Part I (Item 5): Temporary or irregular employment",
        "statutory_scope": "Authorizes evaluation of employment type stability and ongoing income stream characteristics.",
        "lane_1_id": "regb_1002_6_a",
        "lane_2_id": "interp_9_b2_comment2",
    },
    "NAME_EDUCATION_TYPE": {
        "standard_category": "Applicant creditworthiness profile",
        "form_c1_item": "Part I (Item 23): Other pertinent credit evaluation factors",
        "statutory_scope": "Authorizes consideration of pertinent background information not on prohibited bases.",
        "lane_1_id": "regb_1002_6_a",
        "lane_2_id": "regb_1002_9_b_2",
    },
    "NAME_HOUSING_TYPE": {
        "standard_category": "Length or stability of residence",
        "form_c1_item": "Part I (Item 10): Length of residence / living arrangements",
        "statutory_scope": "Authorizes consideration of residence stability and housing obligations.",
        "lane_1_id": "regb_1002_6_a",
        "lane_2_id": "regb_1002_9_b_2",
    },

    # Thin-file / Alternative Data
    "thin_file": {
        "standard_category": "No credit file / Limited credit experience",
        "form_c1_item": "Part I (Item 13 & 14): No credit file / Limited credit experience",
        "statutory_scope": "Authorizes consideration of breadth and depth of applicant credit records and alternative data.",
        "lane_1_id": "regb_1002_6_a",
        "lane_2_id": "circular_2022_03_response",
    },
    "mobile_bill_consistency": {
        "standard_category": "Insufficient alternative credit references",
        "form_c1_item": "Part I (Item 2): Insufficient number of credit references provided",
        "statutory_scope": "Authorizes evaluation of recurring non-traditional utility/telecom cash flow payment consistency.",
        "lane_1_id": "regb_1002_6_a",
        "lane_2_id": "circular_2022_03_response",
    },

    # Credit Accounts / Installments
    "bureau_active_credits_count": {
        "standard_category": "Insufficient number of credit references provided",
        "form_c1_item": "Part I (Item 2): Insufficient number of credit references provided",
        "statutory_scope": "Authorizes evaluation of the number and depth of verified active credit reference accounts.",
        "lane_1_id": "regb_1002_6_a",
        "lane_2_id": "circular_2023_03_response",
    },
    "installments_count": {
        "standard_category": "Limited installment credit experience",
        "form_c1_item": "Part I (Item 14): Limited credit experience",
        "statutory_scope": "Authorizes evaluation of past installment loan volume, experience, and trade line maturity.",
        "lane_1_id": "regb_1002_6_b_6",
        "lane_2_id": "circular_2023_03_response",
    },

    # Prior Bureau Inquiries / Refusals
    "prev_refusal_rate": {
        "standard_category": "Poor credit performance / previous credit denial history",
        "form_c1_item": "Part I (Item 15): Poor credit performance with others / prior credit history",
        "statutory_scope": "Authorizes consideration of prior bureau credit history, credit inquiry frequency, and past credit decisions.",
        "lane_1_id": "regb_1002_6_b_6",
        "lane_2_id": "fcra_1681m_a_1_2",
    },
    "prev_refused_count": {
        "standard_category": "Poor credit performance / previous credit denial history",
        "form_c1_item": "Part I (Item 15): Poor credit performance with others / prior credit history",
        "statutory_scope": "Authorizes consideration of prior bureau credit history and refusal counts.",
        "lane_1_id": "regb_1002_6_b_6",
        "lane_2_id": "fcra_1681m_a_1_2",
    },
    "prev_applications_count": {
        "standard_category": "Number of recent inquiries on credit bureau report",
        "form_c1_item": "Part I (Item 21): Number of recent inquiries on credit bureau report",
        "statutory_scope": "Authorizes consideration of recent credit application inquiry volume and bureau report activity.",
        "lane_1_id": "regb_1002_6_a",
        "lane_2_id": "fcra_1681m_a_3_4",
    },
}

FEATURE_TO_CLAUSE = {
    fname: meta["lane_1_id"] for fname, meta in FEATURE_METADATA.items()
}


# ─── OUTPUT SCHEMA (Pydantic) ─────────────────────────

class RegulatoryBasis(BaseModel):
    clause_id:       str
    citation:        str
    requirement:     str
    statutory_scope: str | None = None


class ReasonCode(BaseModel):
    rank:                 int
    feature_name:         str
    standard_category:    str
    form_c1_item:         str | None = None
    plain_english_reason: str
    lane_1_authorization: RegulatoryBasis
    lane_2_mandate:       RegulatoryBasis
    regulatory_basis:     RegulatoryBasis


class AdverseActionNotice(BaseModel):
    applicant_id:           str
    decision_band:          str
    calibrated_probability: float
    reasons:                list[ReasonCode]
    disclosure_statement:   str


# ─── PROHIBITED TERMS ─────────────────────────────────

PROHIBITED_TERMS = [
    "race", "color", "religion", "national origin", "sex",
    "marital status", "age", "familial status", "disability",
    "public assistance", "gender",
]


# ─── PROMPT TEMPLATE ──────────────────────────────────

GENERATION_PROMPT = """You are a senior compliance officer writing a legally sound Adverse Action Notice under ECOA (Regulation B, 12 CFR Part 1002) and FCRA (15 U.S.C. § 1681m).
Your notice will be reviewed by federal bank regulators (CFPB / OCC).

DUAL-LANE COMPLIANCE RULES:
1. Every reason must correspond EXACTLY to one feature in SHAP_REASONS. Do not invent or omit reasons.
2. Use the provided STANDARD_CATEGORY and FORM_C1_ITEM for each feature.
3. The plain_english_reason must be clear, specific, at an 8th-grade reading level (max 25 words), reflecting the true risk direction:
   - For lower-value risk features (employment_years, installments_count, bureau_active_credits_count, thin_file): phrase as "too few", "too short", "limited", "insufficient", or "lack of established history".
   - For higher-value risk features (late_payment_share, mean_days_late, underpayment_share, credit_income_ratio, annuity_income_ratio, prev_refusal_rate, prev_refused_count): phrase as "too high", "excessive", "frequent", or "elevated".
4. For lane_1_authorization:
   - Use the pre-assigned LANE_1_ID and its exact citation.
   - For `requirement`: copy a complete, substantive legal sentence from the LANE_1_TEXT provided (do NOT copy just a heading or section number).
   - Set `statutory_scope` to the provided STATUTORY_SCOPE string.
5. For lane_2_mandate:
   - Use the pre-assigned LANE_2_ID and its exact citation.
   - For `requirement`: copy a complete, substantive legal sentence from the LANE_2_TEXT provided (do NOT copy just a section symbol or number like "§1681m.").
6. For regulatory_basis: copy the same object as lane_1_authorization.
7. CRITICAL PROTECTED CLASS RULE:
   Never write, quote, or list any prohibited protected-class terms anywhere in ANY output field (including disclosure_statement, reasons, citations, or requirements):
   PROHIBITED: race, color, religion, national origin, sex, marital status, age, familial status, disability, public assistance, gender.
   - For `disclosure_statement`: write a general legal statement without listing protected classes, such as: "Federal law requires creditors to disclose the specific principal reasons for credit decisions. You have the right to obtain the consumer reporting information used in this assessment within 60 days." NEVER enumerate protected demographic categories.
   - If a statutory sentence contains any prohibited term, replace `requirement` with:
     "This regulation governs credit evaluation factors as an authorized basis for adverse action notices."
8. Output ONLY valid JSON matching the schema below. No preamble, no markdown.

OUTPUT SCHEMA:
{{
  "applicant_id": "<string>",
  "decision_band": "<Approve|Refer|Deny>",
  "calibrated_probability": <float>,
  "reasons": [
    {{
      "rank": <1|2|3|4>,
      "feature_name": "<exact feature_name from SHAP_REASONS>",
      "standard_category": "<exact standard_category from SHAP_REASONS>",
      "form_c1_item": "<exact form_c1_item from SHAP_REASONS>",
      "plain_english_reason": "<one sentence, max 25 words>",
      "lane_1_authorization": {{
        "clause_id": "<LANE_1_ID>",
        "citation": "<exact citation for LANE_1_ID>",
        "requirement": "<complete legal sentence from LANE_1_TEXT>",
        "statutory_scope": "<exact statutory_scope from SHAP_REASONS>"
      }},
      "lane_2_mandate": {{
        "clause_id": "<LANE_2_ID>",
        "citation": "<exact citation for LANE_2_ID>",
        "requirement": "<complete legal sentence from LANE_2_TEXT>"
      }},
      "regulatory_basis": {{
        "clause_id": "<LANE_1_ID>",
        "citation": "<exact citation for LANE_1_ID>",
        "requirement": "<complete legal sentence from LANE_1_TEXT>",
        "statutory_scope": "<exact statutory_scope from SHAP_REASONS>"
      }}
    }}
  ],
  "disclosure_statement": "<2-3 sentence formal disclosure explaining statutory rights under ECOA and FCRA>"
}}

---

APPLICANT_ID: {applicant_id}
DECISION_BAND: {decision_band}
CALIBRATED_PROBABILITY: {calibrated_prob}
THIN_FILE: {is_thin_file}

SHAP_REASONS:
{shap_reasons_block}

Write the Adverse Action Notice JSON now."""


# ─── HELPERS ──────────────────────────────────────────

_CLAUSE_TEXT_LIMIT = 500


def _clip_to_last_sentence(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    window = text[:limit]
    last_period = window.rfind(".")
    if last_period == -1:
        return window
    return window[: last_period + 1]


def build_shap_block(shap_features: list[dict], retrieved_clauses: list[dict]) -> str:
    clause_lookup = {c["chunk_id"]: c for c in retrieved_clauses}
    lines = []

    for i, f in enumerate(shap_features, 1):
        fname = f["feature_name"]
        meta = FEATURE_METADATA.get(fname, {
            "standard_category": "Credit evaluation factor",
            "lane_1_id": "regb_1002_6_a",
            "lane_2_id": "regb_1002_9_b_2",
        })

        l1_chunk = clause_lookup.get(meta["lane_1_id"], {})
        l2_chunk = clause_lookup.get(meta["lane_2_id"], {})

        l1_text = _clip_to_last_sentence(l1_chunk.get("text", ""), _CLAUSE_TEXT_LIMIT)
        l2_text = _clip_to_last_sentence(l2_chunk.get("text", ""), _CLAUSE_TEXT_LIMIT)

        if fname in ["employment_years", "installments_count", "bureau_active_credits_count", "thin_file"]:
            dir_hint = "lower values increase default risk (phrase as: too few, limited, short history)"
        else:
            dir_hint = "higher values increase default risk (phrase as: too high, excessive, elevated)"

        lines.append(
            f"{i}. Feature: {fname}\n"
            f"   Value: {f['value']}\n"
            f"   Risk Interpretation: {dir_hint}\n"
            f"   STANDARD_CATEGORY: {meta['standard_category']}\n"
            f"   FORM_C1_ITEM: {meta.get('form_c1_item', 'Part I Checklist Factor')}\n"
            f"   STATUTORY_SCOPE: {meta.get('statutory_scope', 'Statutory authority to evaluate creditworthiness criteria.')}\n"
            f"   LANE_1_ID: {meta['lane_1_id']} | CITATION: {l1_chunk.get('citation', '')}\n"
            f"   LANE_1_TEXT: \"{l1_text}\"\n"
            f"   LANE_2_ID: {meta['lane_2_id']} | CITATION: {l2_chunk.get('citation', '')}\n"
            f"   LANE_2_TEXT: \"{l2_text}\""
        )
    return "\n\n".join(lines)


def check_prohibited_terms(text: str) -> list[str]:
    hits = []
    lower = text.lower()
    for term in PROHIBITED_TERMS:
        if re.search(r"\b" + re.escape(term) + r"\b", lower):
            hits.append(term)
    return hits


def parse_llm_json(raw: str) -> dict:
    cleaned = raw.strip()
    cleaned = re.sub(r"^```json\s*", "", cleaned)
    cleaned = re.sub(r"^```\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned)


# ─── MAIN GENERATE FUNCTION ───────────────────────────

def generate(
    applicant_id:       str,
    decision_band:      str,
    calibrated_prob:    float,
    is_thin_file:       bool,
    shap_features:      list[dict],
    retrieved_clauses:  list[dict]
) -> dict:

    audit_flags = []

    # Build prompt
    shap_block = build_shap_block(shap_features, retrieved_clauses)

    prompt = GENERATION_PROMPT.format(
        applicant_id=applicant_id,
        decision_band=decision_band,
        calibrated_prob=round(calibrated_prob, 4),
        is_thin_file=is_thin_file,
        shap_reasons_block=shap_block,
    )

    # Call Gemini
    model = genai.GenerativeModel(
        model_name=MODEL,
        generation_config=genai.types.GenerationConfig(
            temperature=0.0,
            response_mime_type="application/json"
        )
    )

    response     = model.generate_content(prompt)
    raw_output   = response.text
    notice_dict  = parse_llm_json(raw_output)

    # ── POST-CHECK 1: feature names not hallucinated ──
    valid_features = {f["feature_name"] for f in shap_features}
    for reason in notice_dict.get("reasons", []):
        fname = reason.get("feature_name")
        if fname not in valid_features:
            audit_flags.append(
                f"HALLUCINATED_FEATURE: {fname} not in input SHAP features"
            )

    # ── POST-CHECK 2: citations not hallucinated ──────
    valid_clauses = {c["chunk_id"] for c in retrieved_clauses}
    for reason in notice_dict.get("reasons", []):
        for sub_key in ["lane_1_authorization", "lane_2_mandate", "regulatory_basis"]:
            rb = reason.get(sub_key, {})
            cid = rb.get("clause_id")
            if cid and cid not in valid_clauses:
                audit_flags.append(
                    f"HALLUCINATED_CITATION: {cid} in {sub_key} not in retrieved clauses"
                )

    # ── POST-CHECK 3: prohibited terms in ALL output text fields ──
    fields_to_scan: list[tuple[str, str]] = [
        ("disclosure_statement", notice_dict.get("disclosure_statement", "")),
    ]
    for i, reason in enumerate(notice_dict.get("reasons", [])):
        fields_to_scan.extend([
            (f"reasons[{i}].plain_english_reason", reason.get("plain_english_reason", "")),
            (f"reasons[{i}].standard_category", reason.get("standard_category", "")),
            (f"reasons[{i}].lane_1_authorization.requirement", reason.get("lane_1_authorization", {}).get("requirement", "")),
            (f"reasons[{i}].lane_2_mandate.requirement", reason.get("lane_2_mandate", {}).get("requirement", "")),
        ])

    for field_path, text in fields_to_scan:
        hits = check_prohibited_terms(text)
        if hits:
            audit_flags.append(
                f"PROHIBITED_TERM_IN_OUTPUT | field={field_path} | terms={hits}"
            )

    # ── POST-CHECK 4: SHAP direction respected ─────────
    shap_lookup = {f["feature_name"]: f["shap"] for f in shap_features}
    negative_words = ["low", "short", "insufficient", "lack", "few", "no", "limited"]
    positive_words = ["high", "many", "excessive", "frequent", "elevated", "multiple"]

    for reason in notice_dict.get("reasons", []):
        fname = reason.get("feature_name")
        text = reason.get("plain_english_reason", "").lower()
        val = shap_lookup.get(fname, 0)

        if fname in ["employment_years", "installments_count", "bureau_active_credits_count", "thin_file"] and val > 0:
            if not any(w in text for w in negative_words):
                audit_flags.append(
                    f"SHAP_DIRECTION_MISMATCH: {fname} (low value = risk) "
                    f"reason text does not reflect low/short/limited"
                )

        if fname in ["late_payment_share", "credit_income_ratio", "prev_refusal_rate", "underpayment_share"] and val > 0:
            if not any(w in text for w in positive_words):
                audit_flags.append(
                    f"SHAP_DIRECTION_MISMATCH: {fname} (high value = risk) "
                    f"reason text does not reflect high/excessive/elevated"
                )

    # ── ENRICH WITH CANONICAL METADATA ──────────────
    for reason in notice_dict.get("reasons", []):
        fname = reason.get("feature_name")
        meta = FEATURE_METADATA.get(fname, {})
        if meta:
            if not reason.get("form_c1_item"):
                reason["form_c1_item"] = meta.get("form_c1_item")
            if "lane_1_authorization" in reason and isinstance(reason["lane_1_authorization"], dict):
                if not reason["lane_1_authorization"].get("statutory_scope"):
                    reason["lane_1_authorization"]["statutory_scope"] = meta.get("statutory_scope")
            if "regulatory_basis" in reason and isinstance(reason["regulatory_basis"], dict):
                if not reason["regulatory_basis"].get("statutory_scope"):
                    reason["regulatory_basis"]["statutory_scope"] = meta.get("statutory_scope")

    # ── VALIDATE AGAINST PYDANTIC SCHEMA ──────────────
    notice = AdverseActionNotice(**notice_dict)

    return {
        "notice":      notice.model_dump(),
        "audit_flags": audit_flags
    }


if __name__ == "__main__":
    from rag.retriever import retrieve

    test_shap = [
        {"feature_name": "late_payment_share",   "value": 0.44, "shap": 0.35},
        {"feature_name": "thin_file",            "value": 1,    "shap": 0.31},
        {"feature_name": "employment_years",     "value": 0.5,  "shap": 0.18},
        {"feature_name": "annuity_income_ratio", "value": 0.6,  "shap": 0.11},
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
        calibrated_prob=0.82,
        is_thin_file=True,
        shap_features=test_shap,
        retrieved_clauses=retriever_output["retrieved_clauses"]
    )

    print("\nAdverse Action Notice Generated:")
    print(json.dumps(result["notice"], indent=2))
    print(f"\nAudit Flags ({len(result['audit_flags'])}):")
    for flag in result["audit_flags"]:
        print(f"  ⚠ {flag}")