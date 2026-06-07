from pydantic import BaseModel
from typing import List, Literal, Optional

# 🧑 Crear paciente
class PacienteCrear(BaseModel):
    dni: str
    nombre: str
    sexo: str
    fecha_nacimiento: str
    origen : str
    
class TriajeSchema(BaseModel):
    sintomas: str
    peso: float
    altura: float
    prioridad_ia : float
    
class PacienteActualizar(BaseModel):
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    tipo_sangre: Optional[str] = None
    tiene_tatuajes: Optional[bool] = None
    religion: Optional[str] = None
    contacto_emergencia: Optional[str] = None
    
class EspecialidadRequest(BaseModel):
    especialidad: str
    
        
class MonitoreoSchema(BaseModel):
    presion_arterial: Optional[str] = None
    frecuencia_cardiaca: Optional[int] = None
    saturacion_oxigeno: Optional[int] = None
    temperatura: Optional[float] = None
    observaciones: Optional[str] = None
    
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str