from fastapi import APIRouter, HTTPException
from db.db import get_db

router = APIRouter()

@router.put("/asignar/{caso_id}")
def asignar_recursos(caso_id: int, doctor_id: int, camilla_id: int):
    db = get_db()
    cursor = db.cursor()

    try:
        # validar caso
        cursor.execute("""
            SELECT estado_id FROM casos_emergencia WHERE id = ?
        """, (caso_id,))
        
        caso  = cursor.fetchone()

        if not caso :
            raise HTTPException(404, "Caso no encontrado")

        if caso ["estado_id"] != 3:
            raise HTTPException(400, "El caso no está en atención")

        # asignar recursos
        cursor.execute("""
            SELECT disponibilidad
            FROM doctores
            WHERE id = ?
        """, (doctor_id,))
        
        doctor = cursor.fetchone()
        
        if not doctor:
            raise HTTPException(status_code=404,detail="Doctor no encontrado")
        
        if doctor["disponibilidad"] == 0:
            raise HTTPException(status_code=400,detail="Doctor no disponible")
        
        cursor.execute("""
            SELECT ocupada
            FROM camillas
            WHERE id = ?
        """, (camilla_id,))
        
        camilla = cursor.fetchone()

        if not camilla:
            raise HTTPException(status_code=404,detail="Camilla no encontrada")

        if camilla["ocupada"] == 1:
            raise HTTPException(status_code=400,detail="Camilla ocupada")
        
        cursor.execute("""
            UPDATE casos_emergencia
            SET doctor_id = ?,
                camilla_id = ?
            WHERE id = ?
        """, (
            doctor_id,
            camilla_id,
            caso_id
        ))


        cursor.execute("""
            UPDATE doctores SET disponibilidad = 0 WHERE id = ?
        """, (doctor_id,))

        cursor.execute("""
            UPDATE camillas SET ocupada = 1 WHERE id = ?
        """, (camilla_id,))

        db.commit()

        return {
            "mensaje": "Recursos asignados",
            "caso_id": caso_id,
            "doctor_id": doctor_id,
            "camilla_id": camilla_id
            
        }

    except HTTPException:
        raise
    
    except Exception as e:

        db.rollback()
        print("ERROR asignar_recursos:", e)
        raise HTTPException(status_code=500,detail=str(e))

    finally:
        db.close()