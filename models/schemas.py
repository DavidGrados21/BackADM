from pydantic import BaseModel
from typing import List, Literal, Optional

# 🧑 Crear paciente
class PacienteCrear(BaseModel):
    dni: str
    nombre: str
    sexo: str
    fecha_nacimiento: str


# 🏥 Historial clínico (opcional pero recomendado)
class HistorialClinicoCrear(BaseModel):
    caso_id: int
    alergias: str
    enfermedades: str
    medicamentos: str


# 🚑 Pre-triaje (antes de llegar)
class PreTriajeRequest(BaseModel):
    paciente_id: int
    sintomas: List[str]
    origen: Literal['pre_arribo', 'presencial']

class CasoCrear(BaseModel):
    paciente_id: int
    prioridad: int
    origen: Literal['pre_arribo', 'presencial']

class EstadoActualizar(BaseModel):
    estado: Literal['pendiente', 'en_atencion', 'finalizado']

class AsignacionRequest(BaseModel):
    doctor_id: int
    camilla_id: int
    
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
    
        
class MonitoreoSchema(BaseModel):

    presion_arterial: Optional[str] = None

    frecuencia_cardiaca: Optional[int] = None

    saturacion_oxigeno: Optional[int] = None

    temperatura: Optional[float] = None

    observaciones: Optional[str] = None