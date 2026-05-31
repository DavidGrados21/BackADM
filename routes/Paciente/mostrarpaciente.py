from fastapi import APIRouter, HTTPException
from db.db import get_db

router = APIRouter()

@router.get("/pacientes/{paciente_id}")
def obtener_paciente(paciente_id: int):
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("""
            SELECT *
            FROM pacientes
            WHERE id = ?
        """, (paciente_id,))

        paciente = cursor.fetchone()

        if not paciente:
            raise HTTPException(
                status_code=404,
                detail="Paciente no encontrado"
            )

        return dict(paciente)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        db.close()