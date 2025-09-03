# Paper Check

## A similarity checker for past papers
`I will rewrite this entire repo later`
---

### About this project

This project is designed to analyze academic examination papers for textual similarities, helping educators identify potential plagiarism or repeated content across different papers.

### Features

- PDF file input (WIP)
- Text similarity analysis (WIP)

### Installation

1. Ensure Python 3.10+ is installed
2. Create and activate virtual environment:

```bash
uv venv
.\.venv\Scripts\activate
```

3. Install dependencies:

```bash
uv pip install -e .
```

### Usage

```bash
flet run ./main.py
```

Before you analysis:
Register paper -> OCR and preprocess -> Examine


### Project Structure

```
paper_check/
├── main.py                # Entry point
├── db/                    # Database directory
├── models/                # Data models
├── src/
│   ├── core.py
│   ├── main_utils.py
│   ├── register.py
│   └── xlsx_operations.py
├── pyproject.toml         # Project configuration
├── uv.lock                # Dependency lockfile
└── README.md              # Project documentation
```
