import os
import re
import sys
import logging
from pathlib import Path
import pdfplumber

# Configure UTF-8 output encoding for Windows consoles and suppress font warnings
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

logging.getLogger("pdfminer").setLevel(logging.ERROR)
logging.getLogger("pypdfium2").setLevel(logging.ERROR)

# ─── FILE CONFIGURATION & CLEANING STRATEGIES ─────────

FILE_CONFIG = {
    "Appendix_C_1002.pdf":     "cfpb_web",
    "Comment_1002_9_full.pdf": "cfpb_web",
    "Circular_2022_03.pdf":    "cfpb_web",
    "Circular_2023_03.pdf":    "cfpb_web",
    "15_USC_1681a.pdf":        "govinfo",
    "15_USC_1681g.pdf":        "govinfo",
    "15_USC_1681m.pdf":        "govinfo",
}

# Pre-compiled regex patterns for fast line filtering
RE_TIMESTAMP = re.compile(r'^\d+/\d+/\d+,\s+\d+:\d+\s+(AM|PM)', re.IGNORECASE)
RE_PAGE_NUM = re.compile(r'^\d+/\d+$')


def should_strip_line(line: str, strategy: str) -> bool:
    """
    Determine if a line of text should be stripped based on the cleaning strategy.
    """
    stripped = line.strip()
    if not stripped:
        return True

    # Universal patterns
    if RE_TIMESTAMP.search(stripped):
        return True
    if "https://" in line or "http://" in line:
        return True
    if RE_PAGE_NUM.match(stripped):
        return True

    # Govinfo specific headers / repeated markers
    if strategy == "govinfo":
        if "U.S.C. Title 15" in line:
            return True
        if "COMMERCE AND TRADE" in line:
            return True

    return False


def post_process_text(raw_text: str) -> str:
    """
    Apply post-cleaning rules:
    - Preserve section headings exactly as they appear.
    - Collapse 3 or more consecutive blank lines into exactly 2 blank lines.
    - Preserve single blank lines between paragraphs.
    - Output is raw clean text only.
    """
    # Normalize newline characters
    text = raw_text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Collapse 3 or more consecutive blank lines (4 or more \n) into 2 blank lines (3 \n)
    text = re.sub(r'\n{4,}', '\n\n\n', text)
    
    return text.strip()


def find_pdf_path(raw_dir: Path, filename: str) -> Path | None:
    """
    Locate the PDF file directly in raw_dir or recursively in any subdirectories.
    """
    direct_path = raw_dir / filename
    if direct_path.is_file():
        return direct_path

    matches = list(raw_dir.rglob(filename))
    if matches:
        return matches[0]

    return None


def parse_pdf_file(pdf_path: Path, strategy: str) -> tuple[str, int]:
    """
    Extract text page-by-page with pdfplumber and clean lines according to strategy.
    Returns (cleaned_text, page_count).
    """
    cleaned_pages = []
    with pdfplumber.open(pdf_path) as pdf:
        num_pages = len(pdf.pages)
        for page in pdf.pages:
            page_text = page.extract_text()
            if not page_text:
                continue

            page_lines = []
            for line in page_text.split('\n'):
                if should_strip_line(line, strategy):
                    continue
                page_lines.append(line.rstrip())

            if page_lines:
                cleaned_pages.append('\n'.join(page_lines))

    full_text = '\n\n'.join(cleaned_pages)
    final_text = post_process_text(full_text)
    return final_text, num_pages


def main():
    base_dir = Path(__file__).resolve().parent.parent.parent
    if not (base_dir / "rag").exists():
        base_dir = Path.cwd()

    raw_dir = base_dir / "rag" / "raw"
    parsed_dir = base_dir / "rag" / "parsed"

    parsed_dir.mkdir(parents=True, exist_ok=True)

    print(f"Starting PDF parsing across {len(FILE_CONFIG)} target files...\n")

    for filename, strategy in FILE_CONFIG.items():
        pdf_path = find_pdf_path(raw_dir, filename)

        if not pdf_path or not pdf_path.is_file():
            print(f"[WARNING] Missing input file: {filename} in {raw_dir}. Skipping.")
            continue

        out_name = Path(filename).stem + ".txt"
        out_path = parsed_dir / out_name

        try:
            cleaned_text, pages = parse_pdf_file(pdf_path, strategy)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(cleaned_text)

            char_count = len(cleaned_text)
            try:
                print(f"[PARSED] {filename} → {out_name} | pages: {pages} | chars: {char_count}")
            except UnicodeEncodeError:
                print(f"[PARSED] {filename} -> {out_name} | pages: {pages} | chars: {char_count}")

        except Exception as e:
            print(f"[ERROR] Failed to parse {filename}: {e}")

    print("\nPDF parsing complete. Output saved to rag/parsed/")


if __name__ == "__main__":
    main()
