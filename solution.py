# solution.py
import fitz
import os
import json
import re
import logging

# ----- Configuration -----
INPUT_DIR = "/app/input"
OUTPUT_DIR = "/app/output"

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# ----- Helpers -----

def is_heading_block(text: str) -> bool:
    """
    Return True if this block of text is a candidate heading.
    Filters out pure punctuation/dot leaders, page numbers, repeated RFP lines, headers/footers.
    """
    # Only punctuation or dot leaders
    if re.fullmatch(r'[\s\.\-–]+', text):
        return False
    # Ends with page number
    if re.search(r'\s+\d+$', text):
        return False
    # Common headers/footers
    if text.startswith("Page ") or "Page " in text:
        return False
    if text.startswith("©") or text.startswith("Version "):
        return False
    # Repeated gibberish (e.g. RFP blocks)
    if text.count("RFP:") > 0:
        return False
    return True

def extract_and_classify(pdf_path: str) -> dict:
    """
    Open the PDF at pdf_path, extract and classify headings into H1/H2/H3,
    merge multi-line blocks, and return a dict with 'title' and 'outline'.
    """
    doc = fitz.open(pdf_path)
    outline = []
    title = None

    for page_index in range(doc.page_count):
        page = doc.load_page(page_index)
        blocks = page.get_text("dict")["blocks"]

        first_on_page = True
        prev_level = None

        for block in blocks:
            # Only text blocks
            if block["type"] != 0:
                continue
            # Skip blocks in top-of-page headers
            if block["bbox"][1] < 80:
                continue

            # Merge all spans in all lines of this block
            block_text = " ".join(
                "".join(span["text"] for span in line["spans"]).strip()
                for line in block["lines"]
            ).strip()

            if not block_text or not is_heading_block(block_text):
                continue

            # Detect numbered headings: e.g. "3. Introduction", "2.1 Scope"
            m = re.match(r'^(\d+(?:\.\d+)*\.)\s*(.*)', block_text)
            if m:
                num = m.group(1).rstrip(".")
                content = m.group(2).strip()
                # Single number = H2, nested numbers = H3
                level = "H3" if "." in num else "H2"
                text = f"{m.group(1)} {content}"
            else:
                # Unnumbered: first on page → H1; else H2 or H3 by context
                if first_on_page:
                    level = "H1"
                else:
                    level = "H3" if prev_level == "H2" else "H2"
                text = block_text

            # Capture document title: first H1 on page 1
            if title is None and page_index == 0 and level == "H1":
                title = text
                logger.info(f"Detected title: '{title}'")

            outline.append({
                "level": level,
                "text": text,
                "page": page_index + 1
            })
            logger.info(f"Page {page_index+1}: '{text}' → {level}")

            prev_level = level
            first_on_page = False

    doc.close()
    return {"title": title or "", "outline": outline}

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for fname in sorted(os.listdir(INPUT_DIR)):
        if not fname.lower().endswith(".pdf"):
            continue
        input_path = os.path.join(INPUT_DIR, fname)
        logger.info(f"Processing '{fname}'")
        result = extract_and_classify(input_path)
        out_fname = os.path.splitext(fname)[0] + ".json"
        out_path = os.path.join(OUTPUT_DIR, out_fname)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        logger.info(f"Wrote outline to '{out_fname}'\n")

if __name__ == "__main__":
    main()
