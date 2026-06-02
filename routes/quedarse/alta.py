from fastapi import APIRouter, HTTPException
from db.db import get_db

router = APIRouter()

@router.put("/alta-hospitalaria/{hospitalizacion_id}")
def dar_alta_hospitalaria(hospitalizacion_id: int):

    db = get_db()
    cursor = db.cursor()

    try:

        # =========================
        # 🔍 OBTENER HOSPITALIZACIÓN
        # =========================
        cursor.execute("""
            SELECT
                id,
                caso_id,
                habitacion_id,
                estado
            FROM hospitalizaciones
            WHERE id = ?
        """, (hospitalizacion_id,))

        hospitalizacion = cursor.fetchone()

        if not hospitalizacion:
            raise HTTPException(status_code=404,detail="Hospitalización no encontrada")

        # =========================
        # 🔍 VALIDAR ESTADO
        # =========================
        if hospitalizacion["estado"] != "internado":
            raise HTTPException(
                status_code=400,
                detail="El paciente ya tiene alta médica"
            )

        caso_id = hospitalizacion["caso_id"]
        habitacion_id = hospitalizacion["habitacion_id"]

        # =========================
        # 🏨 DAR ALTA
        # =========================
        cursor.execute("""
            UPDATE hospitalizaciones
            SET
                estado = 'alta',
                fecha_salida = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (hospitalizacion_id,))

        # =========================
        # 🛏️ LIBERAR HABITACIÓN
        # =========================
        if habitacion_id:

            cursor.execute("""
                UPDATE habitaciones
                SET ocupada = 0
                WHERE id = ?
            """, (habitacion_id,))

        # =========================
        # 🚑 FINALIZAR CASO
        # =========================
        cursor.execute("""
            UPDATE casos_emergencia
            SET id_estado = 4
            WHERE id = ?
        """, (caso_id,))

        db.commit()

        return {
            "mensaje": "Alta hospitalaria realizada correctamente",
            "hospitalizacion_id": hospitalizacion_id,
            "caso_id": caso_id,
            "estado": "alta"
        }

    except HTTPException:
        raise

    except Exception as e:
        print("Error alta hospitalaria:", e)

        raise HTTPException(status_code=500,detail="Error al dar alta hospitalaria")
    finally:
        db.close()