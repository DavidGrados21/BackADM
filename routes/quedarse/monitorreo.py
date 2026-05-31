from fastapi import APIRouter, HTTPException
from db.db import get_db
from models.schemas import MonitoreoSchema

router = APIRouter()

@router.post("/monitoreo/{caso_id}")
def registrar_monitoreo(caso_id: int, data: MonitoreoSchema):

    db = get_db()
    cursor = db.cursor()

    try:

        # =========================
        # 🔍 VALIDAR CASO
        # =========================
        cursor.execute("""
            SELECT id
            FROM casos_emergencia
            WHERE id = ?
        """, (caso_id,))

        caso = cursor.fetchone()

        if not caso:
            raise HTTPException(status_code=404,detail="Caso no encontrado")

        # =========================
        # 🏥 VALIDAR HOSPITALIZACIÓN
        # =========================
        cursor.execute("""
            SELECT id
            FROM hospitalizaciones
            WHERE caso_id = ?
              AND estado = 'internado'
        """, (caso_id,))

        hospitalizacion = cursor.fetchone()

        if not hospitalizacion:
            raise HTTPException(status_code=400,detail="El paciente no está hospitalizado")

        # =========================
        # 🩺 REGISTRAR MONITOREO
        # =========================
        cursor.execute("""
            INSERT INTO monitoreo (
                caso_id,
                presion_arterial,
                frecuencia_cardiaca,
                saturacion_oxigeno,
                temperatura,
                observaciones
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            caso_id,
            data.presion_arterial,
            data.frecuencia_cardiaca,
            data.saturacion_oxigeno,
            data.temperatura,
            data.observaciones
        ))

        monitoreo_id = cursor.lastrowid

        db.commit()

        return {
            "mensaje": "Monitoreo registrado correctamente",
            "monitoreo_id": monitoreo_id,
            "caso_id": caso_id
        }

    except HTTPException:
        raise

    except Exception as e:
        print("Error monitoreo:", e)
        raise HTTPException(status_code=500,detail="Error al registrar monitoreo")

    finally:
        db.close()