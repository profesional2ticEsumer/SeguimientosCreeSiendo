from itertools import zip_longest
import os
from typing import Dict, List, Union
from fastapi import APIRouter, Request, Form, HTTPException, logger
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import json
from datetime import datetime
from utils.helpers import require_auth, create_document_structure, load_seguimiento_data, save_seguimiento_data

router = APIRouter()
templates = Jinja2Templates(directory="../../front/templates")
DOCUMENTS_BASE_PATH = "documents"

@router.post("/save-seguimiento/{folder}/{follow_up}")
async def save_seguimiento(
    request: Request,
    doc_number: str,
    doc_adviser: str,
    folder: str,
    follow_up: str,
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
    print(f"doc_number: '{doc_number}'")
    print(f"doc_adviser: '{doc_adviser}'")
    print(f"follow_up: '{follow_up}'")

    # Limpiar posibles guiones bajos al final o espacios
    doc_number = doc_number.strip('_').strip()
    doc_adviser = doc_adviser.strip('_').strip()
    follow_up = follow_up.strip('_').strip()

    require_auth(request)

    doc_path = Path(DOCUMENTS_BASE_PATH) / f"documento_{folder}"
    seguimiento_path = doc_path / follow_up
    seguimiento_path.mkdir(exist_ok=True)

    # Procesar compromisos
    compromisos = []
    for desc, resp, fecha_comp in zip(compromisos_desc, compromisos_resp, compromisos_fecha):
        if desc:
            compromisos.append({
                "descripcion": desc,
                "responsable": resp,
                "fecha": fecha_comp
            })

    # Procesar participantes
    participantes = []
    for nombre, rol, firma in zip(participantes_nombre, participantes_rol, participantes_firma):
        if nombre:
            participantes.append({
                "nombre": nombre,
                "rol": rol,
                "firma": firma
            })

    # Estructura de datos
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

    # Guardar los datos
    save_seguimiento_data(seguimiento_path, seguimiento_data)
    
    return RedirectResponse(url=f"/document/{folder}", status_code=302)

    # return RedirectResponse(url=f"/document/{doc_number}", status_code=302)
    return RedirectResponse(url="/dashboard", status_code=302)

@router.get("/document/{folder}/{follow_up}", response_class=HTMLResponse)
async def view_document(request: Request, folder: str, follow_up: str):
    require_auth(request)
    doc_path = Path(DOCUMENTS_BASE_PATH) / f"documento_{folder}/{follow_up}"
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
        "folder": folder,
        "seguimientos": seguimientos
    })


# @router.post("/crear")
# async def crear_documento(request: Request, doc_id: str):
    require_auth(request)
    create_document_structure(doc_id, request)
    return {"message": "Estructura de documento creada"}

@router.post("/create-document")
async def create_document(doc_number: str = Form(...), request: Request = None):
    require_auth(request)

    user_id = request.cookies.get("user")
    if not user_id:
        raise HTTPException(status_code=403, detail="Usuario no autenticado")

    doc_path = Path(DOCUMENTS_BASE_PATH) / f"documento_{doc_number}_{user_id}"
    
    if doc_path.exists():
        raise HTTPException(status_code=400, detail="El documento ya existe")

    # Crear estructura pasando el doc_number original (sin user_id) y el request
    create_document_structure(doc_number, request)

    # Redirige usando el nombre completo
    full_doc_id = f"{doc_number}_{user_id}"
    return RedirectResponse(url=f"/document/{full_doc_id}/seguimiento_1", status_code=302)

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
    
