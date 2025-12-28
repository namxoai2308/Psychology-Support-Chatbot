from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from urllib.parse import quote
from app.core.database import get_db
from app.core.security import get_current_teacher, get_current_user
from app.models.models import User, SchoolDocument
from app.schemas import DocumentUploadResponse
from app.services.gemini import gemini_service

router = APIRouter(prefix="/api/documents", tags=["Documents"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_school_document(
    file: UploadFile = File(...),
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Upload school PDF document (teacher only)"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Save file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Process PDF and save to database
    # KHÔNG CẦN Gemini Embedding API - không tốn quota!
    try:
        print(f"📄 Starting PDF processing: {file.filename}")
        doc = gemini_service.process_school_pdf(file_path, file.filename, db)
        print(f"✅ PDF processed successfully: {file.filename}")
        print(f"✅ Saved {len(doc.chunks)} chunks to database")
    except Exception as e:
        print(f"❌ Error processing PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing PDF: {str(e)}"
        )
    
    return doc


@router.get("/", response_model=List[DocumentUploadResponse])
def get_documents(
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get all uploaded documents (teacher only)"""
    documents = db.query(SchoolDocument).order_by(
        SchoolDocument.uploaded_at.desc()
    ).all()
    return documents


@router.get("/{document_id}/download")
def download_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    inline: bool = True
):
    """View or download PDF document (students and teachers can access)
    
    Args:
        inline: If True, display PDF in browser. If False, force download.
    """
    document = db.query(SchoolDocument).filter(
        SchoolDocument.id == document_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )
    
    file_path = os.path.join(UPLOAD_DIR, document.filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail="PDF file not found on server"
        )
    
    # Encode filename for HTTP header (RFC 2231 format for Unicode support)
    # Use URL encoding for the filename parameter
    encoded_filename = quote(document.filename.encode('utf-8'), safe='')
    
    # Create ASCII-safe filename fallback (remove non-ASCII chars or replace)
    ascii_filename = document.filename.encode('ascii', 'ignore').decode('ascii')
    if not ascii_filename or ascii_filename != document.filename:
        # If filename has non-ASCII chars, use a safe fallback
        ascii_filename = "document.pdf"
    
    # Set Content-Disposition header with proper encoding (RFC 2231)
    headers = {}
    if inline:
        # Display in browser - use both ASCII fallback and UTF-8 encoded filename
        headers["Content-Disposition"] = f'inline; filename="{ascii_filename}"; filename*=UTF-8\'\'{encoded_filename}'
    else:
        # Force download
        headers["Content-Disposition"] = f'attachment; filename="{ascii_filename}"; filename*=UTF-8\'\'{encoded_filename}'
    
    # Read file and return as Response to avoid encoding issues
    with open(file_path, 'rb') as f:
        file_content = f.read()
    
    return Response(
        content=file_content,
        media_type="application/pdf",
        headers=headers
    )


