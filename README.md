# PDF Outline Extractor

This repository contains a Dockerized Python solution to automatically extract and classify headings from PDF documents into a structured JSON outline.

## Table of Contents

1. [Description](#description)
2. [Project Structure](#project-structure)
3. [Approach](#approach)
4. [Dependencies](#dependencies)
5. [Installation & Build](#installation--build)
6. [Usage](#usage)
7. [Input & Output](#input--output)
8. [JSON Schema](#json-schema)
9. [Example](#example)
10. [Troubleshooting](#troubleshooting)
11. [License](#license)

---

## Description

The PDF Outline Extractor scans all PDF files in the `input/` directory and produces, for each PDF, a JSON file in the `output/` directory containing:

* **Title** (H1) detected on the first page
* **Outline**: a list of headings (H1/H2/H3) with their text and page number

This tool is designed to run offline, in an isolated Docker container, with no external network dependencies at runtime.

---

## Project Structure

```plaintext
├── solution.py      # Main extraction script
├── Dockerfile       # Container build instructions
├── README.md        # This documentation
├── input/           # Mount point for source PDFs (empty)
├── output/          # Mount point for generated JSON (empty)
└── .gitignore       # Ignored files and directories
```

* **solution.py**: Implements PDF parsing using PyMuPDF, applies regex and positional filters to detect headings, and serializes results to JSON.
* **Dockerfile**: Builds a minimal Python 3.10 container (AMD64) with PyMuPDF installed.
* **input/**: Bind-mounted by the user; drop your `*.pdf` files here.
* **output/**: Bind-mounted by the user; the container writes `*.json` here.

---

## Approach

1. **Load PDF**: Open each PDF with PyMuPDF (`fitz`).
2. **Block Extraction**: For each page, retrieve text blocks and skip non-text or header/footer spans.
3. **Heading Detection**:

   * Use regex to match numbered headings (`1.`, `1.1.`, etc.) and classify as H2 (top-level numbers) or H3 (nested numbers).
   * Treat the first qualifying text block on the first page as the document title (H1).
   * For unnumbered blocks, infer H2/H3 based on position and preceding level.
4. **Filtering**: Remove pure punctuation, page numbers, and repeated RFP/document markers.
5. **Output**: Serialize `{"title": ..., "outline": [...]}` to a prettified JSON file.

---

## Dependencies

* **Python**: 3.10
* **PyMuPDF**: tested on version 1.22.4

All dependencies are installed at build time; the runtime container has no internet access.

---

## Installation & Build

Ensure you have Docker installed on your AMD64 (x86\_64) host.

```bash
# Clone the repository
git clone <your-repo-url>.git
cd <repo-directory>

# Build the Docker image (force AMD64 platform)
docker build --platform linux/amd64 -t pdf-outline-extractor:latest .
```

---

## Usage

1. **Prepare Input**

   * Place all your PDFs in the `input/` directory.
2. **Run Container**

   ```bash
   docker run --rm \
     --platform linux/amd64 \
     --network none \
     -v "$(pwd)/input:/app/input" \
     -v "$(pwd)/output:/app/output" \
     pdf-outline-extractor:latest
   ```
3. **Collect Results**

   * Check the `output/` folder for `.json` files matching each PDF.

---

## Input & Output

* **Input**: Any number of `*.pdf` files under `/app/input`.
* **Output**: For each `document.pdf`, a `document.json` is created in `/app/output`.

Each JSON file follows the schema below.

---

## JSON Schema

```json
{
  "title": "string",            // Detected H1 title or empty string
  "outline": [                  // Ordered list of headings
    {
      "level": "H1|H2|H3",    // Heading level
      "text": "string",       // Full text including numbering
      "page": integer           // 1-based page number
    },
    ...
  ]
}
```

* Pretty-printed with 2-space indentation.

---

## Example

Suppose you have `input/sample.pdf`. After running:

```bash
docker run --rm \
  --platform linux/amd64 \
  --network none \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  pdf-outline-extractor:latest
```

You’ll get `output/sample.json`:

```json
{
  "title": "1 Introduction",
  "outline": [
    {"level":"H1","text":"1 Introduction","page":1},
    {"level":"H2","text":"1.1 Problem Statement","page":2},
    {"level":"H3","text":"1.1.1 Scope","page":2},
    ...
  ]
}
```

---

## Troubleshooting

* **No JSON output?**

  * Ensure PDFs are valid and placed in `input/`.
  * Check Docker logs for parsing errors.
* **Timeouts on large PDFs**

  * Confirm script runs in under 10 s on representative files.
* **Heading misclassification**

  * Tweak the regex in `solution.py` to match your numbering style.

