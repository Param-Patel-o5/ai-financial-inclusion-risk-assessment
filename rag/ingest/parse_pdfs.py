"""
PDF Parser for Regulated-Lending RAG System.

Extracts text page by page from regulatory PDFs in rag/raw/,
strips boilerplate headers/footers, sidebar navigation links, and markdown link artifacts,
and saves clean structured text files to rag/parsed/.
"""

import re
from pathlib import Path
import pymupdf as fitz


PDF_FILES = [
    "rag/raw/reg_b/12_CFR_1002_9_2026-09-17.pdf",
    "rag/raw/reg_b/Comment_1002_9_Interpretations_2026-09-21.pdf",
    "rag/raw/reg_b/Appendix_C_2026-09-21.pdf",
    "rag/raw/fcra/15_USC_1681m_2024.pdf",
    "rag/raw/cfpb_circulars/Circular_2022-03_2026-09-21.pdf",
    "rag/raw/cfpb_circulars/Circular_2023-03_2023-09-19.pdf",
]


def is_header_footer_line(line: str) -> bool:
    """Identify boilerplate header/footer lines and sidebar navigation to strip."""
    stripped = line.strip()
    if not stripped:
        return False

    # 1. Page number patterns (e.g., "1", "Page 1", "Page 1 of 5", "1/5", "[1]", "1 of 5")
    if re.match(r"^(\[?\d+\]?|Page\s+\d+(\s+of\s+\d+)?|\d+\s*/\s*\d+|\d+\s+of\s+\d+)$", stripped, re.IGNORECASE):
        return True

    # 2. URLs starting with https://www. or https:// or http://www. or http://
    if re.match(r"^https?://(www\.)?", stripped, re.IGNORECASE):
        return True

    # 3. Government boilerplate header
    if "an official website of the united states government" in stripped.lower() or "an official website" in stripped.lower():
        return True

    # 4. Browser print header timestamps (e.g., "9/21/26, 5:19 PM")
    if re.match(r"^\d{1,2}/\d{1,2}/\d{2,4},\s+\d{1,2}:\d{2}\s+(AM|PM)", stripped, re.IGNORECASE):
        return True

    # 5. Scraped sidebar TOC lines like "Comment for 1002.X - ..." or "View all versions of this regulation"
    if re.match(r"^(Comment for 1002\.\d+|View all versions|Search this regulation|THIS VERSION IS THE CURRENT REGULATION)", stripped, re.IGNORECASE):
        return True

    # 6. Scraped navigation artifacts
    if re.match(r"^(Previous section|Next section|Comment 9\(_\)-5|Subpart [AB] -)", stripped, re.IGNORECASE):
        return True

    return False


def clean_page_text(raw_text: str) -> str:
    """Clean page text by stripping boilerplate header/footer lines, nav links, markdown link artifacts, and normalizing spacing."""
    # Strip markdown link artifacts [text](url) -> text
    cleaned = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', raw_text)

    # Strip bare domain / navigation links in parens: (cfpb.gov/...)
    cleaned = re.sub(r"\(cfpb\.gov[^\)]*\)", "", cleaned)
    cleaned = re.sub(r"\(https?://[^\)]*\)", "", cleaned)

    lines = cleaned.splitlines()
    cleaned_lines = []

    for line in lines:
        if is_header_footer_line(line):
            continue
        line_clean = line.strip()
        if line_clean:
            cleaned_lines.append(line)

    page_text = "\n".join(cleaned_lines)
    # Strip excessive newlines
    page_text = re.sub(r"\n\s*\n\s*\n+", "\n\n", page_text).strip()
    return page_text


def parse_pdf_document(pdf_path: Path) -> tuple[int, str]:
    """Read a PDF using pymupdf and extract joined, cleaned text."""
    doc = fitz.open(pdf_path)
    page_count = len(doc)
    page_texts = []

    for page_idx in range(page_count):
        page = doc[page_idx]
        raw_text = page.get_text("text")
        cleaned = clean_page_text(raw_text)
        if cleaned:
            page_texts.append(cleaned)

    full_text = "\n\n".join(page_texts)
    # Final cleanup on entire document text
    full_text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', full_text)
    full_text = re.sub(r"\(cfpb\.gov[^\)]*\)", "", full_text)
    full_text = re.sub(r"\n\s*\n\s*\n+", "\n\n", full_text).strip()
    doc.close()
    return page_count, full_text


def main(target_files: list[str] = None):
    base_dir = Path(__file__).resolve().parent.parent.parent
    parsed_dir = base_dir / "rag" / "parsed"
    parsed_dir.mkdir(parents=True, exist_ok=True)

    files_to_parse = target_files if target_files else PDF_FILES

    print("=" * 80)
    print("REGULATED LENDING RAG CORPUS — PDF TEXT EXTRACTION")
    print("=" * 80)

    for rel_path in files_to_parse:
        pdf_path = base_dir / rel_path
        if not pdf_path.exists():
            print(f"Error: File not found: {pdf_path}")
            continue

        page_count, full_text = parse_pdf_document(pdf_path)
        char_count = len(full_text)

        # Write parsed text
        stem = pdf_path.stem
        out_file = parsed_dir / f"{stem}.txt"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(full_text)

        first_300 = full_text[:300].replace("\n", " ")

        print(f"\nFilename   : {pdf_path.name}")
        print(f"Output     : rag/parsed/{out_file.name}")
        print(f"Page Count : {page_count}")
        print(f"Char Count : {char_count:,}")
        print(f"First 300  : {first_300}...")
        print("-" * 80)


if __name__ == "__main__":
    main()
