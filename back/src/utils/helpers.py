from typing import Dict
from fastapi import Request, HTTPException
from pathlib import Path
import json

DOCUMENTS_BASE_PATH = "documents"

def is_authenticated(request: Request) -> bool:
    return request.cookies.get("auth") == "true"

def require_auth(request: Request):
    if not is_authenticated(request):
        raise HTTPException(status_code=401, detail="No autenticado")

def create_document_structure(doc_number: str):
    doc_path = Path(DOCUMENTS_BASE_PATH) / f"documento_{doc_number}"
    doc_path.mkdir(exist_ok=True)

    for i in range(1, 9):
        seguimiento_path = doc_path / f"seguimiento_{i}"
        seguimiento_path.mkdir(exist_ok=True)
        (seguimiento_path / "imagenes").mkdir(exist_ok=True)
        comments_file = seguimiento_path / "comentarios.json"
        if not comments_file.exists():
            with open(comments_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
                
def load_seguimiento_data(seguimiento_path: Path) -> Dict:
    """Carga los datos de un seguimiento desde el archivo JSON"""
    data_file = seguimiento_path / "seguimiento.json"
    if data_file.exists():
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_seguimiento_data(seguimiento_path: Path, data: Dict):
    """Guarda los datos de un seguimiento en el archivo JSON"""
    data_file = seguimiento_path / "seguimiento.json"
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
