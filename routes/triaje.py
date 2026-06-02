from fastapi import APIRouter, HTTPException
from db.db import get_db
from models.schemas import TriajeSchema

router = APIRouter()

# =========================
# VALIDACIONES
# =========================

def validar_datos(data):

    if data.peso <= 0:
        raise HTTPException(
            status_code=400,
            detail="Peso inválido"
        )

    if data.altura <= 0:
        raise HTTPException(
            status_code=400,
            detail="Altura inválida"
        )

# =========================
# TRIAJE
# =========================

@router.put("/triaje/{caso_id}")

def realizar_triaje(caso_id: int, data: TriajeSchema):

    db = get_db()
    cursor = db.cursor()

    try:

        validar_datos(data)

        cursor.execute("""
            SELECT id, id_especialidad
            FROM casos_emergencia
            WHERE id = ?
        """, (caso_id,))

        caso = cursor.fetchone()

        if not caso:
            raise HTTPException(status_code=404,detail="Caso no encontrado")
        
        # 2. buscar especialidad por nombre
        cursor.execute("""
            SELECT id_especialidad
            FROM especialidad
            WHERE nombre_especialidad = ?
        """, (data.especialidad,))

        esp = cursor.fetchone()

        if not esp:
            raise HTTPException(404, "Especialidad no encontrada")

        id_especialidad = esp["id_especialidad"]

        # 3. buscar doctor por nombre
        cursor.execute("""
            SELECT id_doctor
            FROM doctor
            WHERE nombre_doctor = ?
            LIMIT 1
        """, (data.doctor,))

        doc = cursor.fetchone()

        if not doc:
            raise HTTPException(404, "Doctor no encontrado")

        id_doctor = doc["id_doctor"]


        # =========================
        # INSERTAR O ACTUALIZAR
        # =========================

        cursor.execute("""

            INSERT INTO triaje (
                caso_id,
                sintomas,
                altura,
                peso,
                prioridad_ia
            )
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(caso_id)
            DO UPDATE SET
                sintomas = excluded.sintomas,
                altura = excluded.altura,
                peso = excluded.peso,
                prioridad_ia = excluded.prioridad_ia

        """, (

            caso_id,
            data.sintomas,
            data.altura,
            data.peso,
            data.prioridad_ia

        ))

        # =========================
        # ACTUALIZAR CASO
        # =========================
        
        cursor.execute("""
            UPDATE casos_emergencia
            SET
                prioridad = ?,
                id_estado = 2,
                id_doctor = ?,
                id_especialidad = ?
            WHERE id = ?
        """, (
            data.prioridad_ia,
            id_doctor,
            id_especialidad,
            caso_id
        ))

        db.commit()

        return {
            "mensaje": "Triaje completado correctamente",
            "caso_id": caso_id,
            "doctor": data.doctor,
            "especialidad": data.especialidad,
            "prioridad": data.prioridad_ia
        }

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(500,str(e))

    finally:
        db.close()