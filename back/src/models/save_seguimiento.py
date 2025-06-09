from pydantic import BaseModel
from typing import List, Optional

class Compromiso(BaseModel):
    descripcion: str
    fecha_cumplimiento: str
    responsable: str

class Participante(BaseModel):
    nombre: str
    rol: str

class SeguimientoData(BaseModel):
    dimensiones: List[str]
    fecha: str
    hora: str
    objetivo: str
    aspectos: str
    avances: str
    retos: str
    oportunidades: str
    compromisos: List[Compromiso]
    participantes: List[Participante]