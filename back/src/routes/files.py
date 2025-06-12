from fastapi import APIRouter, Request, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from typing import List
import shutil
from utils.helpers import require_auth

router = APIRouter()
DOCUMENTS_BASE_PATH = "documents"

@router.post("/upload-file/{doc_number}/{seguimiento_num}")
async def upload_file(request: Request, doc_number: str, seguimiento_num: int, files: List[UploadFile] = File(...)):
    require_auth(request)
    imagenes_path = Path(DOCUMENTS_BASE_PATH) / f"documento_{doc_number}" / f"seguimiento_{seguimiento_num}" / "imagenes"
    imagenes_path.mkdir(parents=True, exist_ok=True)

    uploaded_files = []
    for file in files:
        file_path = imagenes_path / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        uploaded_files.append(file.filename)

    return {"message": f"{len(uploaded_files)} archivos subidos", "files": uploaded_files}

@router.get("/image/{folder}/{seguimiento}/{filename}")
async def get_image(request: Request, folder: str, seguimiento: str, filename: str):
    require_auth(request)
    image_path = Path(DOCUMENTS_BASE_PATH) / f"{folder}" / f"{seguimiento}" / "imagenes" / filename
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    return FileResponse(image_path)