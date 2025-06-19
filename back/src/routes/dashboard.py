import os
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from utils.helpers import require_auth
from pathlib import Path
from utils.dependencies import templates

router = APIRouter()

DOCUMENTS_BASE_PATH = "documents"

@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    require_auth(request)

    user = request.cookies.get("user")
    name = request.cookies.get("name")
    user_role = request.cookies.get("role")
    
    documents = []

    for doc_dir in Path(DOCUMENTS_BASE_PATH).iterdir():
        if doc_dir.is_dir() and doc_dir.name.startswith("documento_") and doc_dir.name.endswith(f"_{user}"):
            # doc_number sin el prefijo y sin el sufijo del user
            base_name = doc_dir.name.replace("documento_", "")
            doc_number = base_name.rsplit("_", 1)[0]
            doc_adviser = base_name.rsplit("_", 1)[1]

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
                "doc_adviser": doc_adviser,
                "doc_number": doc_number,
                "seguimientos": seguimientos
            })
        elif user_role == "superadmin":
            # Si es el administrador, listar todos los documentos
            base_name = doc_dir.name.replace("documento_", "")
            doc_number = base_name.rsplit("_", 1)[0]
            doc_adviser = base_name.rsplit("_", 1)[1]

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
                "doc_adviser": doc_adviser,
                "doc_number": doc_number,
                "seguimientos": seguimientos
            })

    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user,
        "user_role": user_role,
        "documents": documents,
        "name": name
    })

