from fastapi import APIRouter
from db.db import get_db
from models.schemas import EspecialidadRequest

router = APIRouter()


@router.post("/doctores-disponibles")
def doctores_disponibles(data: EspecialidadRequest):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT d.nombre
        FROM doctores d
        JOIN especialidades e
        ON d.especialidad_id = e.id
        WHERE e.nombre = ?
            AND d.disponibilidad = 1
        """, (data.especialidad,))

    doctores = [row[0] for row in cursor.fetchall()]
    conn.close()

    return doctores
