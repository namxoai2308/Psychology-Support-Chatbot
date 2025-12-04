from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from app.core.database import get_db
from app.core.security import get_current_teacher
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


