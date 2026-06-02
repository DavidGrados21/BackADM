from fastapi import APIRouter, HTTPException
from db.db import get_db
from models.schemas import PacienteActualizar

router = APIRouter()

@router.put("/pacientes/{paciente_id}")
def actualizar_paciente(
    dni_paciente: str,
    paciente: PacienteActualizar
):
    db = get_db()
    cursor = db.cursor()

    try:
        # verificar si existe
        cursor.execute("""
            SELECT dni_paciente
            FROM paciente
            WHERE dni_paciente = ?
        """, (dni_paciente,))

        existe = cursor.fetchone()

        if not existe:
            raise HTTPException(
                status_code=404,
                detail="Paciente no encontrado"
            )

        cursor.execute("""
            UPDATE paciente
            SET
                telefono_paciente = ?,
                direccion_paciente = ?,
                tipo_sangre_paciente = ?,
                tiene_tatuajes_paciente = ?,
                religion_paciente = ?,
                contacto_emergencia_paciente = ?
            WHERE dni_paciente = ?
        """, (
            paciente.telefono,
            paciente.direccion,
            paciente.tipo_sangre,
            paciente.tiene_tatuajes,
            paciente.religion,
            paciente.contacto_emergencia,
            dni_paciente
        ))

        db.commit()

        return {
            "mensaje": "Paciente actualizado correctamente"
        }

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        db.close()