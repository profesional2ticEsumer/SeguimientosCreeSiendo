import os
from typing import Dict, List
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import json
from datetime import datetime
from utils.helpers import require_auth, create_document_structure, load_seguimiento_data, save_seguimiento_data

router = APIRouter()
templates = Jinja2Templates(directory="../../front/templates")
DOCUMENTS_BASE_PATH = "documents"

@router.post("/save-seguimiento/{doc_number}/{seguimiento_num}")
async def save_seguimiento(
    request: Request,
    doc_number: str,
    seguimiento_num: int,
    dimensiones: List[str] = Form([]),
    fecha: str = Form(...),
    hora: str = Form(...),
    objetivo: str = Form(...),
    aspectos_abordados: str = Form(...),
    avances: str = Form(...),
    retos: str = Form(...),
    oportunidades: str = Form(...),
    compromisos_desc: List[str] = Form([]),
    compromisos_resp: List[str] = Form([]),
    compromisos_fecha: List[str] = Form([]),
    participantes_nombre: List[str] = Form([]),
    participantes_rol: List[str] = Form([]),
    participantes_firma: List[str] = Form([])
):
    require_auth(request)
    
    doc_path = Path(DOCUMENTS_BASE_PATH) / f"documento_{doc_number}"
    seguimiento_path = doc_path / f"seguimiento_{seguimiento_num}"
    seguimiento_path.mkdir(exist_ok=True)
    
    # Procesar compromisos
    compromisos = []
    for desc, resp, fecha_comp in zip(compromisos_desc, compromisos_resp, compromisos_fecha):
        if desc:  # Solo agregar si hay descripción
            compromisos.append({
                "descripcion": desc,
                "responsable": resp,
                "fecha": fecha_comp
            })
    
    # Procesar participantes
    participantes = []
    for nombre, rol, firma in zip(participantes_nombre, participantes_rol, participantes_firma):
        if nombre:  # Solo agregar si hay nombre
            participantes.append({
                "nombre": nombre,
                "rol": rol,
                "firma": firma
            })
    
    # Crear estructura de datos
    seguimiento_data = {
        "dimensiones": dimensiones,
        "fecha": fecha,
        "hora": hora,
        "objetivo": objetivo,
        "aspectos_abordados": aspectos_abordados,
        "avances": avances,
        "retos": retos,
        "oportunidades": oportunidades,
        "compromisos": compromisos,
        "participantes": participantes,
        "comentarios": load_seguimiento_data(seguimiento_path).get("comentarios", [])
    }
    
    # Guardar datos
    save_seguimiento_data(seguimiento_path, seguimiento_data)
    
    return RedirectResponse(url=f"/document/{doc_number}", status_code=302)

@router.get("/document/{doc_number}/{follow_up}", response_class=HTMLResponse)
async def view_document(request: Request, doc_number: str, follow_up: str):
    require_auth(request)
    doc_path = Path(DOCUMENTS_BASE_PATH) / f"documento_{doc_number}/{follow_up}"
    if not doc_path.exists():
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    seguimientos = []
    
    seguimiento_path = doc_path
    imagenes = [f.name for f in (seguimiento_path / "imagenes").iterdir() if f.is_file()] if seguimiento_path.exists() else []
        
    # Cargar datos del seguimiento
    seguimiento_data = load_seguimiento_data(seguimiento_path)
        
    seguimientos.append({
        "numero": follow_up.replace("seguimiento_", ""),
        "imagenes": imagenes,
        "dimensiones": seguimiento_data.get("dimensiones", []),
        "fecha": seguimiento_data.get("fecha", ""),
        "hora": seguimiento_data.get("hora", ""),
        "objetivo": seguimiento_data.get("objetivo", ""),
        "aspectos": seguimiento_data.get("aspectos_abordados", ""),
        "avances": seguimiento_data.get("avances", ""),
        "retos": seguimiento_data.get("retos", ""),
        "oportunidades": seguimiento_data.get("oportunidades", ""),
        "compromisos": seguimiento_data.get("compromisos", []),
        "participantes": seguimiento_data.get("participantes", []),
        "comentarios": seguimiento_data.get("comentarios", [])
    })

    return templates.TemplateResponse("document.html", {
        "request": request,
        "doc_number": doc_number,
        "seguimientos": seguimientos
    })

# Los demás endpoints (create-document, add-comment, etc.) se mantienen igual

@router.post("/create-document")
async def create_document(doc_number: str = Form(...), request: Request = None):
    require_auth(request)

    doc_path = Path(DOCUMENTS_BASE_PATH) / f"documento_{doc_number}"
    if doc_path.exists():
        raise HTTPException(status_code=400, detail="El documento ya existe")

    create_document_structure(doc_number)
    return RedirectResponse(url=f"/document/{doc_number}", status_code=302)

@router.get("/document/{doc_number}", response_class=HTMLResponse)
async def view_document(request: Request, doc_number: str):
    require_auth(request)
    doc_path = Path(DOCUMENTS_BASE_PATH) / f"documento_{doc_number}"
    if not doc_path.exists():
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    seguimientos = []
    for i in range(1, 9):
        seguimiento_path = doc_path / f"seguimiento_{i}"
        imagenes = [f.name for f in (seguimiento_path / "imagenes").iterdir() if f.is_file()] if seguimiento_path.exists() else []
        comentarios = []

        comments_file = seguimiento_path / "comentarios.json"
        if comments_file.exists():
            with open(comments_file, 'r', encoding='utf-8') as f:
                comentarios = json.load(f)

        seguimientos.append({
            "numero": i,
            "imagenes": imagenes,
            "comentarios": comentarios
        })

    return templates.TemplateResponse("document.html", {
        "request": request,
        "doc_number": doc_number,
        "seguimientos": seguimientos
    })

@router.post("/add-comment/{doc_number}/{seguimiento_num}")
async def add_comment(request: Request, doc_number: str, seguimiento_num: int, comentario: str = Form(...)):
    require_auth(request)
    doc_path = Path(DOCUMENTS_BASE_PATH) / f"documento_{doc_number}"
    comments_file = doc_path / f"seguimiento_{seguimiento_num}" / "comentarios.json"
    comentarios = []

    if comments_file.exists():
        with open(comments_file, 'r', encoding='utf-8') as f:
            comentarios = json.load(f)

    nuevo_comentario = {
        "fecha": datetime.now().isoformat(),
        "usuario": request.cookies.get("user"),
        "comentario": comentario
    }
    comentarios.append(nuevo_comentario)

    with open(comments_file, 'w', encoding='utf-8') as f:
        json.dump(comentarios, f, ensure_ascii=False, indent=2)

    return RedirectResponse(url=f"/document/{doc_number}", status_code=302)

@router.get("/get-seguimiento/{doc_number}/{seguimiento_num}")
async def get_seguimiento_data(doc_number: str, seguimiento_num: str):
    if seguimiento_num.startswith("seguimiento_"):
        num = seguimiento_num.replace("seguimiento_", "")
    else:
        raise HTTPException(status_code=400, detail="Formato de seguimiento inválido")

    # Construcción segura de ruta base
    base_path = os.path.join(os.path.dirname(__file__), '..', 'documents', f'documento_{doc_number}')
    base_path = os.path.abspath(base_path)

    json_path = os.path.join(base_path, f'seguimiento_{num}', 'seguimiento.json')

    if not os.path.exists(json_path):
        json_path = os.path.join(base_path, 'imagenes', 'seguimiento.json')
        if not os.path.exists(json_path):
            raise HTTPException(status_code=404, detail="Archivo de seguimiento no encontrado")

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        comentarios_path = os.path.join(base_path, 'imagenes', 'comentarios.json')
        if os.path.exists(comentarios_path):
            with open(comentarios_path, 'r', encoding='utf-8') as f:
                data['comentarios'] = json.load(f).get(num, [])

        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer el archivo: {str(e)}")
    
@router.get("/seguimiento/{doc_number}/{numero_seguimiento}")
def ver_seguimiento(doc_number: str, numero_seguimiento: int):
    seguimiento = obtener_seguimiento(doc_number, numero_seguimiento)  # Tu lógica aquí

    if seguimiento and seguimiento.estado == "rechazado":
        return templates.TemplateResponse("seguimiento.html", {
            "seguimiento": None,
            "doc_number": doc_number,
            "numero_seguimiento": numero_seguimiento,
            "estado": "rechazado"
        })
    else:
        return templates.TemplateResponse("seguimiento.html", {
            "seguimiento": seguimiento,
            "doc_number": doc_number,
            "numero_seguimiento": numero_seguimiento,
            "estado": "activo"
        })    
