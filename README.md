# Document OCR and Financial Data Extraction System

A simple web-based application that allows users to upload financial documents and automatically extract important information from them using OCR and data processing techniques.

## Features

* Upload financial documents
* Extract text from uploaded documents using OCR
* Identify important financial fields
* Extract values from the document
* Validate extracted financial data
* Perform basic financial calculations and checks
* Display extracted and validated results

## Technologies Used

* Python
* FastAPI
* OCR
* Regular Expressions
* HTML / CSS / JavaScript
* JSON
* Uvicorn

## Project Structure

```text
project/
│
├── app/
│   ├── api/
│   ├── core/
│   ├── services/
│   ├── validators/
│   └── main.py
│
├── static/
│
├── uploads/
│
├── requirements.txt
├── README.md
└── .env
```

## How It Works

```text
Upload Document
       ↓
OCR Processing
       ↓
Text Extraction
       ↓
Field Extraction
       ↓
Financial Validation
       ↓
Display Results
```

## Extracted Information

The system can extract information such as:

* Document date
* Currency
* Financial statement values
* Revenue
* Expenses
* Assets
* Liabilities
* Cash flow values
* Other available financial fields

The extracted fields depend on the uploaded document.

## Validation

After extracting the information, the system performs validation checks on the financial values.

For example:

```text
Extracted Values
       ↓
Apply Validation Rules
       ↓
Compare Calculated and Reported Values
       ↓
Show Validation Result
```

The system can identify values that are correct, inconsistent, or require further checking.

## Installation

Clone the project and open the project folder.

Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Running the Application

Start the application using:

```bash
uvicorn app.main:app --reload
```

Then open the application in your browser.

```text
http://127.0.0.1:8000
```

## Uploading a Document

1. Open the application.
2. Select a financial document.
3. Upload the document.
4. Wait for OCR processing.
5. The extracted information will be displayed.
6. The system performs validation on the extracted financial values.

## Purpose

The main purpose of this project is to reduce manual work involved in reading financial documents and checking important financial information.

It combines OCR, text processing, field extraction, and validation to make financial document analysis easier.

## Note

This project is developed for academic and learning purposes.
