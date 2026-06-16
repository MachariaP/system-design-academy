# Testing Guide

This project is primarily a Markdown-based curriculum with inline code snippets (Python, TypeScript). While there are no standalone `.py` or `.ts` files currently, the following testing strategies apply:

## Current Testing Approach

- **Inline code snippets** are copied into scratch files and run manually against the dependencies in `requirements.txt`.
- **Mermaid diagrams** should be validated for syntax correctness (most Markdown renderers support this natively).
- **Cross-references** (internal links between modules, Docs, and blueprints) should be verified to ensure no broken links.

## Planned Testing Infrastructure

1. **Markdown linting** — Use `markdownlint` to enforce consistent formatting, heading structure, and style rules.
2. **Link validation** — Use `lychee` or a similar tool to check all internal and external links.
3. **Code extraction and testing** — Extract code blocks from markdown files into standalone Python scripts and run them with pytest.
4. **Diagram validation** — Validate Mermaid diagram syntax programmatically.

## Running Tests

```bash
# Install dependencies
pip install -r requirements.txt

# Future: extract and test code blocks
# python scripts/extract_and_test.py modules/
```

## Test Coverage Goals

- All Mermaid diagrams render without errors.
- All internal links resolve to existing files.
- All Python code snippets are syntactically valid.
- All TypeScript code snippets are syntactically valid.
