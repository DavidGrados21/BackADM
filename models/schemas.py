from pydantic import BaseModel
from typing import List, Literal, Optional

class PacienteCrear(BaseModel):
    dni: str
    nombre: str
    sexo: str
    fecha_nacimiento: str
    origen : str
    id_especialidad: int
    
class TriajeSchema(BaseModel):
    sintomas: str
    peso: float
    altura: float
    prioridad_ia : float
    doctor: str
    especialidad: str
    
class PacienteActualizar(BaseModel):
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    tipo_sangre: Optional[str] = None
    tiene_tatuajes: Optional[bool] = None
    religion: Optional[str] = None
    contacto_emergencia: Optional[str] = None
    
class EspecialidadRequest(BaseModel):
    especialidad: str
    
class LoginDoctor(BaseModel):
    correo: str
    password: str
    
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str