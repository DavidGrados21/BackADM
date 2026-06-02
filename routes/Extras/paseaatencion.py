from fastapi import APIRouter, HTTPException
from db.db import get_db

router = APIRouter()

@router.put("/pasar-a-atencion/{caso_id}")
def pasar_a_atencion(caso_id: int):
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("""
            SELECT id_estado
            FROM casos_emergencia
            WHERE id = ?
        """, (caso_id,))
        
        caso  = cursor.fetchone()

        if not caso :
            raise HTTPException(404, "Caso no encontrado")

        if caso ["id_estado"] != 2:
            raise HTTPException(400, "El paciente no está en pendiente")

        # 🔄 solo cambiar estado
        cursor.execute("""
            UPDATE casos_emergencia
            SET id_estado = 3
            WHERE id = ?
        """, (caso_id,))

        db.commit()

        return {
            "mensaje": "Paciente en atención (sin asignación aún)",
            "caso_id": caso_id,
            "estado": 3
        }

    except HTTPException:
        raise
    
    except Exception as e:
        db.rollback()
        print("ERROR pasar_a_atencion:", e)
        raise HTTPException(status_code=500,detail=str(e))

    finally:
        db.close()