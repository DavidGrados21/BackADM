from fastapi import APIRouter, HTTPException
from db.db import get_db

router = APIRouter()


@router.post("/hospitalizar/{caso_id}")
def hospitalizar_paciente(caso_id: int, habitacion_id: int):

    db = get_db()
    cursor = db.cursor()

    try:

        # =========================
        # 🔍 VERIFICAR CASO
        # =========================
        cursor.execute("""
            SELECT 
                id,
                estado_id
            FROM casos_emergencia
            WHERE id = ?
        """, (caso_id,))

        caso = cursor.fetchone()

        if not caso:
            raise HTTPException(status_code=404,detail="Caso no encontrado")

        # ✅ debe estar en atención
        if caso["estado_id"] != 3:
            raise HTTPException(status_code=400,detail="El paciente no está en atención")

        # =========================
        # 🔍 VALIDAR HABITACIÓN
        # =========================
        cursor.execute("""
            SELECT 
                id,
                ocupada
            FROM habitaciones
            WHERE id = ?
        """, (habitacion_id,))

        habitacion = cursor.fetchone()

        if not habitacion:
            raise HTTPException(status_code=404,detail="Habitación no encontrada")

        if habitacion["ocupada"] == 1:
            raise HTTPException(status_code=400,detail="La habitación ya está ocupada")

        # =========================
        # 🔍 VALIDAR SI YA EXISTE
        # =========================
        cursor.execute("""
            SELECT id
            FROM hospitalizaciones
            WHERE caso_id = ?
              AND estado = 'internado'
        """, (caso_id,))

        hospitalizacion = cursor.fetchone()

        if hospitalizacion:
            raise HTTPException(status_code=400,detail="El paciente ya está hospitalizado"
            )

        # =========================
        # 🏨 CREAR HOSPITALIZACIÓN
        # =========================
        cursor.execute("""
            INSERT INTO hospitalizaciones (
                caso_id,
                habitacion_id,
                estado
            )
            VALUES (?, ?, 'internado')
        """, (
            caso_id,
            habitacion_id
        ))

        hospitalizacion_id = cursor.lastrowid

        # =========================
        # 🛏️ OCUPAR HABITACIÓN
        # =========================
        cursor.execute("""
            UPDATE habitaciones
            SET ocupada = 1
            WHERE id = ?
        """, (habitacion_id,))

        db.commit()

        return {
            "mensaje": "Paciente hospitalizado correctamente",
            "hospitalizacion_id": hospitalizacion_id,
            "caso_id": caso_id,
            "habitacion_id": habitacion_id,
            "estado": "internado"
        }

    except HTTPException:
        raise

    except Exception as e:
        print("Error hospitalización:", e)
        raise HTTPException(status_code=500,detail="Error al hospitalizar paciente")

    finally:
        db.close()