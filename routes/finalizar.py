from fastapi import APIRouter, HTTPException
from db.db import get_db

router = APIRouter()

@router.put("/finalizar/{caso_id}")
def finalizar_atencion(caso_id: int):
    db = get_db()
    cursor = db.cursor()

    try:
        # 🔍 obtener datos del caso
        cursor.execute("""
            SELECT estado_id, doctor_id, camilla_id
            FROM casos_emergencia
            WHERE id = ?
        """, (caso_id,))
        
        caso  = cursor.fetchone()

        if not caso :
            raise HTTPException(404, "Caso no encontrado")

        if caso ["estado_id"] != 3:
            raise HTTPException(400, "El caso no está en atención")

        doctor_id = caso ["doctor_id"]
        camilla_id = caso ["camilla_id"]

        # 🔄 cambiar estado a finalizado
        cursor.execute("""
            UPDATE casos_emergencia
            SET estado_id = 4
            WHERE id = ?
        """, (caso_id,))

        # 🧑‍⚕️ liberar doctor (si existe)
        if doctor_id is not None:
            cursor.execute("""
                UPDATE doctores
                SET disponibilidad = 1
                WHERE id = ?
            """, (doctor_id,))

        # 🛏️ liberar camilla (si existe)
        if camilla_id is not None:
            cursor.execute("""
                UPDATE camillas
                SET ocupada = 0
                WHERE id = ?
            """, (camilla_id,))

        db.commit()

        return {
            "mensaje": "Atención finalizada y recursos liberados",
            "caso_id": caso_id,
            "estado": 4
        }

    except HTTPException:
        raise
    
    except Exception as e:
        db.rollback()
        print("ERROR finalizar_atencion:", e)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()