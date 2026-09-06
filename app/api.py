"""HTTP API for normalizing and comparing contractor estimate PDFs."""

from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.comparison import compare_estimates
from app.ai_extractor import configured_ai_extractor
from app.normalizer import normalize_estimate
from app.pdf_text import PdfExtractionError
from app.trades import UnsupportedTradeError, get_trade_profile, supported_trades


MAX_FILE_SIZE = 10 * 1024 * 1024

app = FastAPI(
    title="Vendor Quote Normalizer API",
    description="Normalize and compare contractor estimate PDFs.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, object]:
    """Confirm that the API server is running."""
    return {
        "status": "ok",
        "ai_enabled": configured_ai_extractor() is not None,
        "supported_trades": supported_trades(),
    }


async def _save_uploaded_pdf(upload: UploadFile) -> Path:
    """Validate an uploaded PDF and save it temporarily for processing."""
    filename = upload.filename or ""
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    content = await upload.read()
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded PDF is empty.")
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="The uploaded PDF exceeds the 10 MB limit.",
        )

    with NamedTemporaryFile(delete=False, suffix=".pdf") as temporary_file:
        temporary_file.write(content)
        return Path(temporary_file.name)


def _delete_temporary_files(*paths: Path) -> None:
    for path in paths:
        path.unlink(missing_ok=True)


@app.post("/estimates/normalize")
async def normalize_uploaded_estimate(
    estimate: UploadFile = File(...),
    trade: str = Form("painting"),
) -> dict:
    """Normalize one uploaded contractor estimate."""
    try:
        get_trade_profile(trade)
    except UnsupportedTradeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    temporary_path = await _save_uploaded_pdf(estimate)
    try:
        return normalize_estimate(
            temporary_path,
            configured_ai_extractor(),
            trade,
        )
    except PdfExtractionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    finally:
        _delete_temporary_files(temporary_path)


@app.post("/estimates/compare")
async def compare_uploaded_estimates(
    first_estimate: UploadFile = File(...),
    second_estimate: UploadFile = File(...),
    trade: str = Form("painting"),
) -> dict:
    """Normalize and compare two uploaded contractor estimates."""
    try:
        get_trade_profile(trade)
    except UnsupportedTradeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    first_path = await _save_uploaded_pdf(first_estimate)
    try:
        second_path = await _save_uploaded_pdf(second_estimate)
    except Exception:
        _delete_temporary_files(first_path)
        raise

    try:
        return compare_estimates(
            first_path,
            second_path,
            configured_ai_extractor(),
            trade,
        )
    except PdfExtractionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    finally:
        _delete_temporary_files(first_path, second_path)
