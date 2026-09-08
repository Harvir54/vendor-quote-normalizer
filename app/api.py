"""HTTP API for normalizing and comparing contractor estimate documents."""

from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.comparison import compare_estimates, compare_many_estimates
from app.ai_extractor import configured_ai_extractor
from app.normalizer import normalize_estimate
from app.pdf_text import PdfExtractionError
from app.trades import UnsupportedTradeError, get_trade_profile, supported_trades


MAX_PDF_SIZE = 10 * 1024 * 1024
MAX_IMAGE_SIZE = 8 * 1024 * 1024
SUPPORTED_UPLOADS = {
    ".pdf": MAX_PDF_SIZE,
    ".jpg": MAX_IMAGE_SIZE,
    ".jpeg": MAX_IMAGE_SIZE,
    ".png": MAX_IMAGE_SIZE,
    ".heic": MAX_IMAGE_SIZE,
    ".heif": MAX_IMAGE_SIZE,
}

app = FastAPI(
    title="Vendor Quote Normalizer API",
    description="Normalize and compare contractor estimate PDFs and images.",
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


def _matches_signature(suffix: str, content: bytes) -> bool:
    if suffix == ".pdf":
        return content.startswith(b"%PDF")
    if suffix in {".jpg", ".jpeg"}:
        return content.startswith(b"\xff\xd8\xff")
    if suffix == ".png":
        return content.startswith(b"\x89PNG\r\n\x1a\n")
    if suffix in {".heic", ".heif"}:
        return len(content) >= 12 and content[4:8] == b"ftyp" and content[8:12] in {
            b"heic", b"heix", b"hevc", b"hevx", b"mif1", b"msf1"
        }
    return False


async def _save_uploaded_document(upload: UploadFile) -> Path:
    """Validate an uploaded document and save it temporarily for processing."""
    filename = upload.filename or ""
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_UPLOADS:
        raise HTTPException(
            status_code=400,
            detail="Supported files are PDF, JPG, JPEG, PNG, HEIC, and HEIF.",
        )

    content = await upload.read()
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded document is empty.")
    size_limit = SUPPORTED_UPLOADS[suffix]
    if len(content) > size_limit:
        raise HTTPException(
            status_code=413,
            detail=(
                "The uploaded PDF exceeds the 10 MB limit."
                if suffix == ".pdf"
                else "The uploaded image exceeds the 8 MB limit."
            ),
        )
    if not _matches_signature(suffix, content):
        raise HTTPException(
            status_code=400,
            detail="The file contents do not match its extension.",
        )

    with NamedTemporaryFile(delete=False, suffix=suffix) as temporary_file:
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
    temporary_path = await _save_uploaded_document(estimate)
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
    first_path = await _save_uploaded_document(first_estimate)
    try:
        second_path = await _save_uploaded_document(second_estimate)
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


@app.post("/estimates/compare-many")
async def compare_many_uploaded_estimates(
    estimates: list[UploadFile] = File(...),
    trade: str = Form("painting"),
) -> dict:
    """Normalize and compare between two and five contractor estimates."""
    try:
        get_trade_profile(trade)
    except UnsupportedTradeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not 2 <= len(estimates) <= 5:
        raise HTTPException(
            status_code=400,
            detail="Upload between 2 and 5 estimate documents.",
        )

    temporary_paths: list[Path] = []
    try:
        for estimate in estimates:
            temporary_paths.append(await _save_uploaded_document(estimate))
        return compare_many_estimates(
            temporary_paths,
            configured_ai_extractor(),
            trade,
        )
    except PdfExtractionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    finally:
        _delete_temporary_files(*temporary_paths)
