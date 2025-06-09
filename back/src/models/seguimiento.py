from pydantic import BaseModel
from typing import List, Optional

class Compromiso(BaseModel):
    descripcion: str
    fecha_cumplimiento: str
    responsable: str

class Participante(BaseModel):
    nombre: str
    rol: str

class Comentario(BaseModel):
    autor: str
    contenido: str
    fecha: str

class SeguimientoResponse(BaseModel):
    numero: str
    imagenes: List[str] = []
    dimensiones: List[str] = []
    fecha: Optional[str] = None
    hora: Optional[str] = None
    objetivo: Optional[str] = None
    aspectos: Optional[str] = None
    avances: Optional[str] = None
    retos: Optional[str] = None
    oportunidades: Optional[str] = None
    compromisos: List[Compromiso] = []
    participantes: List[Participante] = []
    comentarios: List[Comentario] = []