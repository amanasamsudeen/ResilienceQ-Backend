from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from schemas.assessment import AssessmentSubmission
from database import get_db
from utils.excel_export import generate_excel
from pathlib import Path

router = APIRouter(prefix="/assessment", tags=["Assessment"])

BASE_DIR = Path(__file__).resolve().parent.parent
EXPORT_DIR = BASE_DIR / "exports"


@router.post("/submit")
def submit_assessment(
    payload: AssessmentSubmission,
    db: Session = Depends(get_db),
):
    file_path = generate_excel(payload)

    return {
        "message": "Assessment submitted successfully",
        "excel_path": file_path.name,  # return filename only
    }


@router.get("/download")
def download_latest_excel():
    files = list(EXPORT_DIR.glob("resilienceq_*.xlsx"))

    if not files:
        raise HTTPException(status_code=404, detail="No assessment file found")

    latest_file = max(files, key=lambda f: f.stat().st_mtime)

    return FileResponse(
        path=latest_file,
        filename=latest_file.name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
