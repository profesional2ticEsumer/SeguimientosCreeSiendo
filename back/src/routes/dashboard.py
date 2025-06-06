import os
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from utils.helpers import require_auth
from pathlib import Path
from utils.dependencies import templates

router = APIRouter()
# templates = Jinja2Templates(directory="../../front/templates")
DOCUMENTS_BASE_PATH = "documents"

@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# @router.get("/dashboard", response_class=HTMLResponse)
# async def dashboard(request: Request):
#     require_auth(request)

#     documents = []
#     for doc_dir in Path(DOCUMENTS_BASE_PATH).iterdir():
#         if doc_dir.is_dir() and doc_dir.name.startswith("documento_"):
#             documents.append(doc_dir.name.replace("documento_", ""))

#     return templates.TemplateResponse("dashboard.html", {
#         "request": request,
#         "user": request.cookies.get("user"),
#         "documents": documents
#     })

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    # Autenticación requerida (debes tener esta función)
    require_auth(request)

    user = request.cookies.get("user")  # Puedes cambiar esto según tu sistema de auth
    documents = []

    for doc_dir in Path(DOCUMENTS_BASE_PATH).iterdir():
        if doc_dir.is_dir() and doc_dir.name.startswith("documento_"):
            doc_number = doc_dir.name.replace("documento_", "")
            seguimientos = []

            for item in os.listdir(doc_dir):
                if item.startswith("seguimiento_"):
                    seg_num = item.split("_")[1]
                    seg_path = doc_dir / item

                    enviado = (seg_path / "seguimiento.json").exists()

                    seguimientos.append({
                        "id": item,
                        "numero": seg_num,
                        "enviado": enviado
                    })

            seguimientos.sort(key=lambda x: int(x["numero"]))

            documents.append({
                "doc_number": doc_number,
                "seguimientos": seguimientos
            })

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "documents": documents
    })
