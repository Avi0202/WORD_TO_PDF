# Document Converter and Merger

A web application that allows users to:
- Convert Word documents to PDF
- Convert PDF documents to Word
- Merge two PDF files into one

## Features

- **Word to PDF Conversion**: Upload a Word document (.doc or .docx) and get a converted PDF
- **PDF to Word Conversion**: Upload a PDF file and get a converted Word document (.docx)
- **PDF Merger**: Upload two PDF files and get a single merged PDF file

## Requirements

- Python 3.7+
- Dependencies (listed in requirements.txt)

## Installation

1. Clone this repository or download the source code

2. Create a virtual environment (recommended):
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - MacOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

1. Start the server:
   ```
   python -m app.main
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:8000
   ```

## Usage

1. **Word to PDF**:
   - Click on the "Word to PDF" section
   - Upload a Word document
   - Click "Convert to PDF"
   - Wait for the conversion to complete
   - The converted file will be automatically downloaded

2. **PDF to Word**:
   - Click on the "PDF to Word" section
   - Upload a PDF file
   - Click "Convert to Word"
   - Wait for the conversion to complete
   - The converted file will be automatically downloaded

3. **Merge PDFs**:
   - Click on the "Merge PDFs" section
   - Upload the first PDF file
   - Upload the second PDF file
   - Click "Merge PDFs"
   - Wait for the merging to complete
   - The merged file will be automatically downloaded

## Technologies Used

- **Backend**: Python, FastAPI
- **Frontend**: HTML, CSS, JavaScript
- **Document Processing**:
  - docx2pdf (Word to PDF)
  - pdf2docx (PDF to Word)
  - PyPDF2 (PDF Merging)

## Notes

- The application creates a temporary directory to store files during processing. This directory is cleaned up when the server shuts down.
- For large files, conversion may take longer. Please be patient.
- Word to PDF conversion might work best on Windows because it uses Microsoft Word under the hood. For other platforms, consider using LibreOffice or additional configurations. 