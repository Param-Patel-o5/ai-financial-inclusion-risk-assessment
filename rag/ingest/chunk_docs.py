"""
Legally-Structured Dynamic Chunking Pipeline for Regulated-Lending RAG System.

Dynamically extracts the 14 targeted regulatory chunks from parsed text files in
rag/parsed/ using exact anchor boundaries, validates token counts, and generates:
- rag/chunks.json (machine-readable corpus for SQLite/ChromaDB indexing)
- rag/chunks_preview.txt (human-readable preview with audit metadata)
"""

import json
import re
from pathlib import Path


def token_count(text: str) -> int:
    """Approximate token count using whitespace word splitting."""
    return len(text.split())


def extract_section(
    full_text: str,
    start_pattern: str,
    end_pattern: str | None,
    chunk_id: str,
    source_filename: str
) -> str:
    """
    Extract substring between start_pattern and end_pattern.
    Raises ValueError if start_pattern is not found.
    """
    start_match = re.search(start_pattern, full_text, re.IGNORECASE | re.DOTALL)
    if not start_match:
        raise ValueError(
            f"Extraction failed for chunk '{chunk_id}': start pattern '{start_pattern}' "
            f"not found in {source_filename}"
        )

    start_pos = start_match.start()

    if end_pattern:
        # Search for end pattern strictly after the start pattern match
        end_match = re.search(end_pattern, full_text[start_match.end():], re.IGNORECASE | re.DOTALL)
        if not end_match:
            raise ValueError(
                f"Extraction failed for chunk '{chunk_id}': end pattern '{end_pattern}' "
                f"not found after start in {source_filename}"
            )
        end_pos = start_match.end() + end_match.start()
        extracted = full_text[start_pos:end_pos]
    else:
        extracted = full_text[start_pos:]

    # Clean extracted snippet
    cleaned = extracted.strip()
    # Normalize excessive newlines
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned


# ─── 14 TARGET CHUNKS SPECIFICATION ───────────────────

CHUNK_SPECS = [
    # ── LANE 1: SUBSTANTIVE FACTOR AUTHORIZATION ──────
    {
        "chunk_id": "regb_1002_6_a",
        "source_file": "Comment_1002_9_full.txt",
        "citation": "12 CFR § 1002.6(a)",
        "lane": 1,
        "features_backed": ["employment_years", "NAME_INCOME_TYPE", "NAME_EDUCATION_TYPE", "NAME_HOUSING_TYPE"],
        "heading": "Rules Concerning Evaluation of Applications — General Rule",
        "start_pattern": r"Except as otherwise provided in the Act and this part,\s+a creditor may consider any information",
        "end_pattern": r"\(b\)\s+Specific rules concerning use of information\.",
    },
    {
        "chunk_id": "regb_1002_6_b_5",
        "source_file": "Comment_1002_9_full.txt",
        "citation": "12 CFR § 1002.6(b)(5)",
        "lane": 1,
        "features_backed": ["credit_income_ratio", "annuity_income_ratio", "AMT_CREDIT", "AMT_INCOME_TOTAL", "AMT_ANNUITY"],
        "heading": "Rules Concerning Evaluation of Applications — Income",
        "start_pattern": r"A creditor shall not discount or exclude from consideration",
        "end_pattern": r"\(6\)\s+Credit history\.",
    },
    {
        "chunk_id": "regb_1002_6_b_6",
        "source_file": "Comment_1002_9_full.txt",
        "citation": "12 CFR § 1002.6(b)(6)",
        "lane": 1,
        "features_backed": ["late_payment_share", "mean_days_late", "max_days_late", "underpayment_share"],
        "heading": "Rules Concerning Evaluation of Applications — Credit History",
        "start_pattern": r"To the extent that a creditor considers credit history",
        "end_pattern": r"\(7\)\s+Immigration status\.",
    },
    {
        "chunk_id": "appendix_c_form_c1_denial_reasons",
        "source_file": "Appendix_C_1002.txt",
        "citation": "12 CFR Part 1002, App. C (Form C-1)",
        "lane": 1,
        "features_backed": [
            "late_payment_share", "mean_days_late", "max_days_late", "underpayment_share",
            "credit_income_ratio", "annuity_income_ratio", "employment_years", "thin_file"
        ],
        "heading": "Sample Form C-1 — Principal Reason(s) for Adverse Action Taken",
        "start_pattern": r"Part I\s*-\s*Principal Reason\(s\)\s+for\s+Credit Denial",
        "end_pattern": r"Part II\s*-\s*Disclosure of Use of Information",
    },

    # ── LANE 2: SPECIFICITY & AI COMPLIANCE MANDATES ───
    {
        "chunk_id": "appendix_c_comment3",
        "source_file": "Appendix_C_1002.txt",
        "citation": "12 CFR Part 1002, App. C, Comment 3",
        "lane": 2,
        "features_backed": ["bureau_active_credits_count", "installments_count", "thin_file", "mobile_bill_consistency"],
        "heading": "Official Interpretation App. C — Sample Forms Illustrative",
        "start_pattern": r"The sample forms are illustrative and may not be appropriate",
        "end_pattern": r"4\.\s+If the reasons listed on the forms are not the factors actually used",
    },
    {
        "chunk_id": "appendix_c_comment4",
        "source_file": "Appendix_C_1002.txt",
        "citation": "12 CFR Part 1002, App. C, Comment 4",
        "lane": 2,
        "features_backed": ["bureau_active_credits_count", "installments_count", "thin_file", "mobile_bill_consistency"],
        "heading": "Official Interpretation App. C — Factors Actually Scored",
        "start_pattern": r"If the reasons listed on the forms are not the factors actually used",
        "end_pattern": r"5\.\s+A creditor may design its own notification forms",
    },
    {
        "chunk_id": "regb_1002_9_b_2",
        "source_file": "Comment_1002_9_full.txt",
        "citation": "12 CFR § 1002.9(b)(2)",
        "lane": 2,
        "features_backed": ["credit_income_ratio", "annuity_income_ratio", "AMT_CREDIT", "AMT_INCOME_TOTAL", "AMT_ANNUITY"],
        "heading": "Notifications — Statement of Specific Reasons",
        "start_pattern": r"The statement of reasons for adverse action required by paragraph",
        "end_pattern": r"\(c\)\s+Incomplete applications",
    },
    {
        "chunk_id": "interp_9_b2_comment2",
        "source_file": "Comment_1002_9_full.txt",
        "citation": "12 CFR Part 1002 (Supp. I), § 1002.9, Comment 9(b)(2)-2",
        "lane": 2,
        "features_backed": ["employment_years", "NAME_INCOME_TYPE"],
        "heading": "Official Interpretation § 1002.9 — Source of Specific Reasons",
        "start_pattern": r"The specific reasons disclosed under",
        "end_pattern": r"3\.\s+Description of reasons\.",
    },
    {
        "chunk_id": "interp_9_b2_comment4",
        "source_file": "Comment_1002_9_full.txt",
        "citation": "12 CFR Part 1002 (Supp. I), § 1002.9, Comment 9(b)(2)-4",
        "lane": 2,
        "features_backed": ["late_payment_share", "mean_days_late", "max_days_late", "underpayment_share"],
        "heading": "Official Interpretation § 1002.9 — Credit Scoring System Reasons",
        "start_pattern": r"If a creditor bases the denial or other adverse action",
        "end_pattern": r"5\.\s+Credit scoring",
    },
    {
        "chunk_id": "interp_9_b2_comment9",
        "source_file": "Comment_1002_9_full.txt",
        "citation": "12 CFR Part 1002 (Supp. I), § 1002.9, Comment 9(b)(2)-9",
        "lane": 2,
        "features_backed": ["prev_refusal_rate", "prev_refused_count", "prev_applications_count"],
        "heading": "Official Interpretation § 1002.9 — Combined ECOA-FCRA Disclosures",
        "start_pattern": r"The ECOA requires disclosure of the principal reasons",
        "end_pattern": r"9\(c\)\s+Incomplete applications\.",
    },
    {
        "chunk_id": "fcra_1681m_a_1_2",
        "source_file": "15_USC_1681m.txt",
        "citation": "15 U.S.C. § 1681m(a)(1)-(2)",
        "lane": 2,
        "features_backed": ["prev_refusal_rate", "prev_refused_count"],
        "heading": "Duties of Users Taking Adverse Actions — Notice & Credit Score Disclosure",
        "start_pattern": r"If any person takes any adverse action with respect to any consumer that is based in whole or in\s+part on any information contained in a consumer report",
        "end_pattern": r"\(3\)\s+provide to the consumer orally",
    },
    {
        "chunk_id": "fcra_1681m_a_3_4",
        "source_file": "15_USC_1681m.txt",
        "citation": "15 U.S.C. § 1681m(a)(3)-(4)",
        "lane": 2,
        "features_backed": ["prev_applications_count"],
        "heading": "Duties of Users Taking Adverse Actions — CRA Identity & Dispute Rights",
        "start_pattern": r"\(3\)\s+provide to the consumer orally, in writing, or electronically",
        "end_pattern": r"\(b\)\s+Adverse action based on information obtained from third parties",
    },
    {
        "chunk_id": "circular_2022_03_response",
        "source_file": "Circular_2022_03.txt",
        "citation": "CFPB Circular 2022-03",
        "lane": 2,
        "features_backed": ["thin_file", "mobile_bill_consistency"],
        "heading": "CFPB Circular 2022-03 — Complex Algorithms & Specific Reasons Mandate",
        "start_pattern": r"ECOA and Regulation B require creditors to provide statements of specific reasons",
        "end_pattern": r"Analysis\s+ECOA makes it unlawful",
    },
    {
        "chunk_id": "circular_2023_03_response",
        "source_file": "Circular_2023_03.txt",
        "citation": "CFPB Circular 2023-03",
        "lane": 2,
        "features_backed": ["bureau_active_credits_count", "installments_count"],
        "heading": "CFPB Circular 2023-03 — Specificity Standard for AI/ML Credit Models",
        "start_pattern": r"(?:No,\s+)?creditors may not rely on the checklist of reasons",
        "end_pattern": r"Analysis\s+The Equal Credit Opportunity Act",
    },
]


def build_chunks(parsed_dir: Path) -> list[dict]:
    """Extract and validate all 14 chunks dynamically from parsed text files."""
    file_cache: dict[str, str] = {}
    chunks: list[dict] = []

    for spec in CHUNK_SPECS:
        fname = spec["source_file"]
        if fname not in file_cache:
            file_path = parsed_dir / fname
            if not file_path.exists():
                raise FileNotFoundError(f"Parsed file missing: {file_path}")
            with open(file_path, "r", encoding="utf-8") as f:
                file_cache[fname] = f.read()

        text = extract_section(
            full_text=file_cache[fname],
            start_pattern=spec["start_pattern"],
            end_pattern=spec["end_pattern"],
            chunk_id=spec["chunk_id"],
            source_filename=fname
        )

        tokens = token_count(text)

        # Quality Gates
        if tokens < 20:
            raise ValueError(
                f"Chunk '{spec['chunk_id']}' text is too short ({tokens} tokens). "
                f"Check start/end boundary anchors."
            )
        if tokens > 450:
            print(f"[WARNING] Chunk '{spec['chunk_id']}' is long: {tokens} tokens.")

        chunk_data = {
            "chunk_id": spec["chunk_id"],
            "source_file": spec["source_file"],
            "citation": spec["citation"],
            "lane": spec["lane"],
            "features_backed": spec["features_backed"],
            "heading": spec["heading"],
            "text": text,
            "token_count": tokens,
        }
        chunks.append(chunk_data)

    return chunks


def main():
    base_dir = Path(__file__).resolve().parent.parent.parent
    if not (base_dir / "rag").exists():
        base_dir = Path(__file__).resolve().parent
    if not (base_dir / "rag").exists():
        base_dir = Path.cwd()

    parsed_dir = base_dir / "rag" / "parsed"
    chunks_json_path = base_dir / "rag" / "chunks.json"
    preview_path = base_dir / "rag" / "chunks_preview.txt"

    print("=" * 60)
    print("Running Dynamic Regulatory Chunking Pipeline (14 Target Chunks)")
    print("=" * 60)

    chunks = build_chunks(parsed_dir)

    print(f"\nExtracted {len(chunks)} / {len(CHUNK_SPECS)} target chunks successfully.\n")

    # Write chunks.json
    with open(chunks_json_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    print(f"[SAVED] {chunks_json_path} ({len(chunks)} chunks)")

    # Write chunks_preview.txt
    preview_lines = [
        "=" * 70,
        "FAIRTRACE REGULATORY CORPUS — 14 TARGET CHUNKS PREVIEW",
        "=" * 70,
        "",
    ]
    for c in chunks:
        preview_lines.append(f"CHUNK ID:        {c['chunk_id']}")
        preview_lines.append(f"CITATION:        {c['citation']}")
        preview_lines.append(f"LANE:            Lane {c['lane']}")
        preview_lines.append(f"FEATURES BACKED: {', '.join(c['features_backed'])}")
        preview_lines.append(f"HEADING:         {c['heading']}")
        preview_lines.append(f"SOURCE FILE:     {c['source_file']}")
        preview_lines.append(f"TOKEN COUNT:     {c['token_count']} tokens")
        preview_lines.append("-" * 70)
        preview_lines.append(c["text"])
        preview_lines.append("=" * 70)
        preview_lines.append("")

    with open(preview_path, "w", encoding="utf-8") as f:
        f.write("\n".join(preview_lines))
    print(f"[SAVED] {preview_path}")

    # Summary table
    print("\nExtraction Summary:")
    print(f"{'Chunk ID':<35} | {'Lane':<5} | {'Tokens':<7} | {'Citation'}")
    print("-" * 75)
    for c in chunks:
        print(f"{c['chunk_id']:<35} | {c['lane']:<5} | {c['token_count']:<7} | {c['citation']}")
    print("-" * 75)


if __name__ == "__main__":
    main()
