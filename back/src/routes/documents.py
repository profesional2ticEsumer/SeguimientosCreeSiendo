from itertools import zip_longest
import os
from typing import Dict, List, Union
from fastapi import APIRouter, Request, Form, HTTPException, logger
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import json
from datetime import datetime
from utils.helpers import require_auth, create_document_structure, load_seguimiento_data, save_seguimiento_data
from models.seguimiento import SeguimientoResponse, Compromiso, Participante
from models.save_seguimiento import SeguimientoData
from models.documents import DocumentCreate

from utils.generate_pdf import PDFGenerator

pdf_generator = PDFGenerator()

router = APIRouter()
templates = Jinja2Templates(directory="../../front/templates")
DOCUMENTS_BASE_PATH = "documents"

@router.get("/get-seguimiento/{folder}/{follow_up}", response_model= SeguimientoResponse)
async def get_seguimiento(folder: str, follow_up: str, request: Request):
    """Obtiene los datos de un seguimiento específico"""
    require_auth(request)

    doc_path = Path(DOCUMENTS_BASE_PATH) / f"{folder}/{follow_up}"
    if not doc_path.exists():
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    seguimiento_path = doc_path
    imagenes = [f.name for f in (seguimiento_path / "imagenes").iterdir() if f.is_file()] if seguimiento_path.exists() else []
        
    # Cargar datos del seguimiento
    seguimiento_data = load_seguimiento_data(seguimiento_path)

    # Convertir compromisos
    compromisos = [
        Compromiso(
            descripcion=c["descripcion"],
            fecha_cumplimiento=c["fecha_cumplimiento"],
            responsable=c["responsable"]
        ) for c in seguimiento_data.get("compromisos", [])
    ]
    
    # Convertir participantes
    participantes = [
        Participante(
            nombre=p["nombre"],
            rol=p["rol"]
        ) for p in seguimiento_data.get("participantes", [])
    ]
    
    # Convertir comentarios
    # comentarios = [
    #     Comentario(
    #         autor=c["autor"],
    #         contenido=c["contenido"],
    #         fecha=c["fecha"]
    #     ) for c in seguimiento_data.get("comentarios", [])
    # ]
        
    return SeguimientoResponse(
        numero=follow_up.replace("seguimiento_", ""),
        imagenes=imagenes,
        dimensiones=seguimiento_data.get("dimensiones", []),
        fecha=seguimiento_data.get("fecha"),
        hora=seguimiento_data.get("hora"),
        objetivo=seguimiento_data.get("objetivo"),
        aspectos=seguimiento_data.get("aspectos"),
        avances=seguimiento_data.get("avances"),
        retos=seguimiento_data.get("retos"),
        oportunidades=seguimiento_data.get("oportunidades"),
        compromisos=compromisos,
        participantes=participantes
        # comentarios=comentarios
    )

@router.post("/create-document")
async def create_document(document_data: DocumentCreate, request: Request):
    require_auth(request)
    user_id = request.cookies.get("user")
    if not user_id:
        raise HTTPException(status_code=403, detail="Usuario no autenticado")
    
    doc_path = Path(DOCUMENTS_BASE_PATH) / f"documento_{document_data.doc_number}_{user_id}"
    if doc_path.exists():
        raise HTTPException(status_code=400, detail="El documento ya existe")
    
    # Crear estructura de archivos
    create_document_structure(document_data.doc_number, request)

    # Crear JSON con los datos de la familia
    apellido = document_data.apellido.lower().replace(" ", "_")
    json_path = doc_path / f"familia_{apellido}.json"
    json_content = {
        "apellido": document_data.apellido,
        "doc_number": document_data.doc_number,
        "creado_por": user_id
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_content, f, ensure_ascii=False, indent=4)
    
    full_doc_id = f"{document_data.doc_number}_{user_id}"
    return {
        "success": True,
        "message": "Documento creado exitosamente",
        "doc_number": document_data.doc_number,
        "full_doc_id": full_doc_id,
        "redirect_url": f"/document/{full_doc_id}/seguimiento_1"
    }

@router.post("/save-seguimiento/{folder}/{follow_up}")
async def save_seguimiento(
    folder: str,
    follow_up: str,
    data: SeguimientoData,
    request: Request
):
    """Guarda los datos de un seguimiento"""
    require_auth(request)
    user_id = request.cookies.get("user")

    if not user_id:
        raise HTTPException(status_code=403, detail="Usuario no autenticado")
    
    seguimiento_path = Path(DOCUMENTS_BASE_PATH) / f"{folder}/{follow_up}"
    if not seguimiento_path.exists():
        raise HTTPException(status_code=404, detail="Seguimiento no encontrado")

    # Cargar datos del seguimiento existente
    seguimiento_data = data.dict()

    # result = pdf_generator.create_reporte_pdf(seguimiento_data)

    # Guardar datos del seguimiento
    save_seguimiento_data(seguimiento_path, seguimiento_data)
    
    # Determinar el siguiente seguimiento
    next_seguimiento = int(follow_up.replace("seguimiento_", "")) + 1
    max_seguimientos = 8  # Número total de seguimientos
    
    return {
        "success": True,
        "next_seguimiento": next_seguimiento if next_seguimiento <= max_seguimientos else None,
        "message": "Datos guardados exitosamente"
    }


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

@router.delete("/delete-document/{folder}")
async def delete_document(folder: str, request: Request):
    """
    Elimina carpeta de un documento y todos sus seguimientos
    
    Args:
        folder: nombre de la carpeta del documento a eliminar
        
    Returns:
        Mensaje de éxito o error
    """
    require_auth(request)
    
    doc_path = Path(DOCUMENTS_BASE_PATH) / f"{folder}"
    
    if not doc_path.exists():
        raise HTTPException(status_code=404, detail="Seguimiento no encontrado")
    
    try:
        # Eliminar el directorio del seguimiento
        for item in doc_path.iterdir():
            if item.is_file():
                item.unlink()
            else:
                os.rmdir(item)
        os.rmdir(doc_path)
        
        return JSONResponse(status_code=200, content={"message": "Seguimiento eliminado exitosamente"})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar el seguimiento: {str(e)}")

@router.get("/download-pdf/{folder}/{filename}")
async def download_pdf(folder: str, filename: str):
    """
    Endpoint para descargar un archivo PDF
    
    Args:
        folder: Carpeta donde se encuentra el archivo PDF
        filename: Nombre del archivo PDF a descargar
        
    Returns:
        Archivo PDF como respuesta de descarga
    """
    try:
        # Verificar que el archivo existe
        doc_path = Path(DOCUMENTS_BASE_PATH) / f"{folder}/{filename}"
        if not doc_path.exists():
            raise HTTPException(status_code=404, detail="Documento no encontrado")

        # Cargar datos del seguimiento existente
        seguimiento_path = doc_path

        seguimiento_data = load_seguimiento_data(seguimiento_path)

        result = pdf_generator.create_reporte_pdf(seguimiento_data)
        
        print(f"Generando PDF: {result['filename']} en {result['file_path']}")

        # Retornar archivo para descarga
        return FileResponse(
            path=result['file_path'],
            filename=result['filename'],
            media_type='application/pdf',
            headers={"Content-Disposition": f"attachment; filename={result['filename']}"}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error descargando archivo: {str(e)}")
