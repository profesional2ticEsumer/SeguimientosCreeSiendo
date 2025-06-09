from typing import Dict
from fastapi import Request, HTTPException
from pathlib import Path
import json

DOCUMENTS_BASE_PATH = "documents"

def is_authenticated(request: Request) -> bool:
    auth_value = request.cookies.get("auth")
    print(f"Cookie 'auth': {auth_value}")  # Para depuración
    return auth_value == "true"

def require_auth(request: Request):
    if not is_authenticated(request):
        raise HTTPException(status_code=401, detail="Usuario no autenticado")

def create_document_structure(doc_number: str, request: Request):
    user_id = request.cookies.get("user")
    if not user_id:
        raise HTTPException(status_code=400, detail="Usuario no especificado en cookies")

    doc_path = Path(DOCUMENTS_BASE_PATH) / f"documento_{doc_number}_{user_id}"
    doc_path.mkdir(exist_ok=True, parents=True)

    for i in range(1, 9):
        seguimiento_path = doc_path / f"seguimiento_{i}"
        seguimiento_path.mkdir(exist_ok=True)
        (seguimiento_path / "imagenes").mkdir(exist_ok=True)

        comments_file = seguimiento_path / "comentarios.json"
        if not comments_file.exists():
            with open(comments_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)

def load_seguimiento_data(seguimiento_path: Path) -> Dict:
    data_file = seguimiento_path / "seguimiento.json"
    if data_file.exists():
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_seguimiento_data(seguimiento_path: Path, data: Dict) -> bool:
    """
    Guarda los datos de seguimiento en un archivo JSON de forma segura.
    
    Args:
        seguimiento_path: Ruta al directorio donde se guardará el archivo
        data: Diccionario con los datos a guardar
        
    Returns:
        bool: True si se guardó correctamente, False si hubo error
        
    Raises:
        OSError: Si hay problemas con el sistema de archivos
        TypeError: Si los datos no son serializables a JSON
    """
    try:
        # Crear el directorio si no existe
        seguimiento_path.mkdir(parents=True, exist_ok=True)
        
        # Definir la ruta del archivo
        data_file = seguimiento_path / "seguimiento.json"
        
        # Guardar en archivo temporal primero (patrón atómico)
        temp_file = seguimiento_path / "seguimiento.tmp"
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Renombrar el archivo temporal al nombre final (operación atómica)
        temp_file.replace(data_file)
        
        return True
        
    except json.JSONEncodeError as e:
        raise TypeError(f"Los datos no son serializables a JSON: {str(e)}")
    except OSError as e:
        raise OSError(f"No se pudo guardar el archivo: {str(e)}")
    except Exception as e:
        raise Exception(f"Error inesperado al guardar: {str(e)}")

# def save_seguimiento_data(seguimiento_path: Path, data: Dict):
#     data_file = seguimiento_path / "seguimiento.json"
#     with open(data_file, 'w', encoding='utf-8') as f:
#         json.dump(data, f, ensure_ascii=False, indent=2)
