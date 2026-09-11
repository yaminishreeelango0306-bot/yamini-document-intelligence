# Architecture

```text
Browser Dashboard
      |
      v
FastAPI REST API
      |
      +--> Document Validation
      |       - type / MIME
      |       - size
      |       - readability
      |       - page count <= 3
      |
      +--> OCR Service
      |       - PDF -> page images -> Tesseract
      |       - JPG/PNG -> Tesseract
      |
      +--> Extraction Service
      |       - field aliases
      |       - table/line-item extraction
      |       - evidence + page number
      |       - additional financial lines
      |
      +--> Financial Validation
      |       - invoice reconciliation
      |       - balance sheet equation
      |       - P&L equations
      |       - cash flow equations
      |
      +--> Repository
      |       - SQLite persistence
      |
      +--> Structured JSON
              |
              v
        Dashboard / Swagger
```
