from fastapi import APIRouter, HTTPException
from db.db import get_db
from models.schemas import LoginDoctor

router = APIRouter(prefix="/doctor",tags=["Doctor"])

@router.post("/login")
def login_doctor(data: LoginDoctor):
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("""
            SELECT
                id_doctor,
                nombre_doctor,
                especialidad_id,
                email_doctor
            FROM doctor
            WHERE email_doctor = ?
              AND password_doctor = ?
        """, (data.correo, data.password))

        doctor = cursor.fetchone()

        if not doctor:
            raise HTTPException(
                status_code=401,
                detail="Correo o contraseña incorrectos"
            )

        return {
            "mensaje": "Login exitoso",
            "doctor": {
                "id_doctor": doctor["id_doctor"],
                "nombre": doctor["nombre_doctor"],
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        db.close()