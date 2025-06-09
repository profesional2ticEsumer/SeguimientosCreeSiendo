from pydantic import BaseModel

class DocumentCreate(BaseModel):
    doc_number: str
    apellido: str

