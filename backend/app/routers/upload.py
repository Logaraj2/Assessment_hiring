from fastapi import APIRouter, HTTPException, UploadFile, File

from app.services.file_parser import parse_resume

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """Upload a resume file (PDF, DOCX, TXT) and extract text."""
    try:
        contents = await file.read()
        text = parse_resume(contents, file.filename)
        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from the file.")
        return {"text": text}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse file: {str(e)}")
