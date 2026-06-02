from fastapi import APIRouter, HTTPException
from db.db import get_db

router = APIRouter()

@router.get("/pacientes")
def listar_pacientes():
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("""
            SELECT 
                dni_paciente,
                nombre_paciente
            FROM paciente
            ORDER BY created_at DESC
        """)

        pacientes = cursor.fetchall()

        return [
            {
                "dni": row["dni_paciente"],
                "nombre": row["nombre_paciente"],
            }
            for row in pacientes
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        db.close()