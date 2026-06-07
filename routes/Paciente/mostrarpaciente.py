from fastapi import APIRouter, HTTPException
from db.db import get_db

router = APIRouter()

@router.get("/pacientes/{dni_paciente}")
def obtener_paciente(dni_paciente: str):
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("""
            SELECT *
            FROM paciente
            WHERE dni_paciente = ?
        """, (dni_paciente,))

        paciente = cursor.fetchone()

        if not paciente:
            raise HTTPException(
                status_code=404,
                detail="Paciente no encontrado"
            )

        return dict(paciente)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno: {str(e)}"
        )

    finally:
        db.close()