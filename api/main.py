import os
import shutil
from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from typing import List
import uuid

# For Word to PDF conversion
from docx2pdf import convert

# For PDF to Word conversion
from pdf2docx import Converter

# For PDF merging
try:
    from PyPDF2 import PdfMerger  # For newer versions of PyPDF2
except ImportError:
    try:
        from PyPDF2 import PdfFileMerger as PdfMerger  # For older versions
    except ImportError:
        from pyPdf import PdfFileMerger as PdfMerger  # Very old versions

app = FastAPI(title="Document Converter and Merger")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="app/templates")

# Create temporary directory for file operations
os.makedirs("temp", exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/convert/word-to-pdf")
async def convert_word_to_pdf(file: UploadFile = File(...)):
    # Validate file
    if not file.filename.endswith(('.docx', '.doc')):
        raise HTTPException(status_code=400, detail="Only Word documents are accepted")
    
    # Save uploaded file
    temp_input_path = f"temp/{file.filename}"
    with open(temp_input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Generate output path
    output_filename = file.filename.rsplit('.', 1)[0] + ".pdf"
    temp_output_path = f"temp/{output_filename}"
    
    try:
        # Convert Word to PDF
        convert(temp_input_path, temp_output_path)
        
        # Return the converted file
        return FileResponse(
            path=temp_output_path,
            filename=output_filename,
            media_type="application/pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")
    finally:
        # Clean up
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)

@app.post("/convert/pdf-to-word")
async def convert_pdf_to_word(file: UploadFile = File(...)):
    # Validate file
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    
    # Save uploaded file
    temp_input_path = f"temp/{file.filename}"
    with open(temp_input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Generate output path
    output_filename = file.filename.rsplit('.', 1)[0] + ".docx"
    temp_output_path = f"temp/{output_filename}"
    
    try:
        # Convert PDF to Word
        cv = Converter(temp_input_path)
        cv.convert(temp_output_path)
        cv.close()
        
        # Return the converted file
        return FileResponse(
            path=temp_output_path,
            filename=output_filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")
    finally:
        # Clean up
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)

@app.post("/merge/pdf")
async def merge_pdfs(files: List[UploadFile] = File(...)):
    # Create a unique temp directory for this operation
    session_id = str(uuid.uuid4())
    temp_dir = os.path.abspath(os.path.join("temp", f"merge_{session_id}"))
    os.makedirs(temp_dir, exist_ok=True)
    print(f"Created temporary directory for this merge operation: {temp_dir}")
    
    # Validate files
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="Please upload at least 2 PDF files")
    
    for file in files:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    
    # Save uploaded files with absolute paths
    temp_input_paths = []
    output_path = None
    
    try:
        for file in files:
            # Clean filename to avoid path issues
            safe_filename = os.path.basename(file.filename).replace('/', '_').replace('\\', '_')
            temp_path = os.path.join(temp_dir, safe_filename)
            print(f"Saving uploaded file to: {temp_path}")
            
            # Ensure the file gets written completely
            content = await file.read()
            with open(temp_path, "wb") as buffer:
                buffer.write(content)
                
            # Verify the file exists and has content
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                print(f"Uploaded file saved successfully: {temp_path} ({os.path.getsize(temp_path)} bytes)")
                temp_input_paths.append(temp_path)
            else:
                print(f"WARNING: File not saved correctly: {temp_path}")
                
        if len(temp_input_paths) < 2:
            raise HTTPException(status_code=400, detail="Not enough valid PDF files were uploaded")
        
        # Generate output path with absolute path
        output_filename = "merged.pdf"
        output_path = os.path.join(temp_dir, output_filename)
        print(f"Output will be saved to: {output_path}")
        
        # Merge PDFs
        print(f"Starting PDF merge with {len(temp_input_paths)} files")
        merger = PdfMerger()
        for path in temp_input_paths:
            print(f"Appending: {path}")
            merger.append(path)
        
        print(f"Writing merged PDF to: {output_path}")
        merger.write(output_path)
        merger.close()
        
        # Verify file exists before returning
        if not os.path.exists(output_path):
            print(f"ERROR: Output file not found at {output_path}")
            raise HTTPException(status_code=500, detail="Failed to create merged PDF file")
        
        file_size = os.path.getsize(output_path)
        print(f"Successfully created merged PDF at: {output_path} ({file_size} bytes)")
        
        if file_size == 0:
            print("ERROR: Created PDF has zero size")
            raise HTTPException(status_code=500, detail="Generated PDF file is empty")
        
        # Important: Return a copy of the file that won't be deleted
        # until after the response is sent
        response = FileResponse(
            path=output_path,
            filename=output_filename,
            media_type="application/pdf",
            background=None  # Don't run in background to ensure file isn't deleted too early
        )
        
        # Don't delete the output file - let the FileResponse handle it
        return response
        
    except Exception as e:
        # Log the error for debugging
        print(f"Error merging PDFs: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return a proper JSON error response
        raise HTTPException(status_code=500, detail=f"Merging failed: {str(e)}")
    finally:
        # Clean up input files but not the output file
        for path in temp_input_paths:
            try:
                if path != output_path and os.path.exists(path):
                    os.remove(path)
                    print(f"Cleaned up input file: {path}")
            except Exception as e:
                print(f"Error cleaning up {path}: {str(e)}")

@app.on_event("startup")
async def startup_event():
    # Create the temp directory if it doesn't exist
    os.makedirs("temp", exist_ok=True)
    print("Application started. Temp directory created at:", os.path.abspath("temp"))

@app.on_event("shutdown")
async def shutdown_event():
    # Clean up temp directory
    temp_dir = os.path.abspath("temp")
    if os.path.exists(temp_dir):
        try:
            # List all files before deleting
            files = os.listdir(temp_dir)
            print(f"Cleaning up temp directory with {len(files)} files: {temp_dir}")
            for file in files:
                try:
                    file_path = os.path.join(temp_dir, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f"Removed file: {file_path}")
                except Exception as e:
                    print(f"Error removing file {file}: {str(e)}")
            
            shutil.rmtree(temp_dir)
            print(f"Removed temp directory: {temp_dir}")
        except Exception as e:
            print(f"Error cleaning up temp directory: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 