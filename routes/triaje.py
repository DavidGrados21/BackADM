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

def realizar_triaje(
    caso_id: int,
    data: TriajeSchema
):

    db = get_db()
    cursor = db.cursor()

    try:

        validar_datos(data)

        cursor.execute("""
            SELECT id
            FROM casos_emergencia
            WHERE id = ?
        """, (caso_id,))

        caso = cursor.fetchone()

        if not caso:

            raise HTTPException(
                status_code=404,
                detail="Caso no encontrado"
            )

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
                estado_id = 2

            WHERE id = ?

        """, (

            data.prioridad_ia,
            caso_id

        ))

        db.commit()

        return {

            "mensaje":
                "Triaje completado correctamente",

            "caso_id":
                caso_id,

            "prioridad":
                data.prioridad_ia,

            "estado":
                "pendiente"

        }

    except HTTPException:

        raise

    except Exception as e:

        db.rollback()

        print(
            "ERROR triaje:",
            e
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        db.close()