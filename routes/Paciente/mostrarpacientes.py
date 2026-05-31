from fastapi import APIRouter, HTTPException
from db.db import get_db

router = APIRouter()

@router.get("/pacientes")
def listar_pacientes():
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("""
            SELECT id, nombre, dni
            FROM pacientes
            ORDER BY id DESC
        """)

        pacientes = cursor.fetchall()

        return [
            {
                "id": row["id"],
                "nombre": row["nombre"],
                "dni": row["dni"]
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