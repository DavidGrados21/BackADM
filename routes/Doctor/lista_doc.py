from fastapi import APIRouter
from db.db import get_db
from models.schemas import EspecialidadRequest

router = APIRouter()

@router.post("/doctores-disponibles")
def doctores_disponibles(data: EspecialidadRequest):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT d.nombre_doctor
        FROM doctor d
        JOIN especialidad e
            ON d.especialidad_id = e.id_especialidad
        WHERE e.nombre_especialidad = ?
    """, (data.especialidad,))


    doctores = [row[0] for row in cursor.fetchall()]
    
    conn.close()

    return doctores
