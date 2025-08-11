# Paper Check

## A similarity checker for past papers

---

### About this project

This project is designed to analyze academic examination papers for textual similarities, helping educators identify potential plagiarism or repeated content across different papers.

### Features

- Excel file input/output support (WIP)
- Text similarity analysis

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

WIP

### Project Structure

```
paper_check/
├── main.py                # Entry point
├── db/                    # Database directory
├── models/                # Data models
├── src/
│   ├── xlsx_operations.py # Excel file handling
│   └── unwrap.py          # Text processing utilities
├── pyproject.toml         # Project configuration
├── uv.lock                # Dependency lockfile
└── README.md              # Project documentation
```

### Dependencies

1. llama_cpp
2. pandas
3. openpyxl
