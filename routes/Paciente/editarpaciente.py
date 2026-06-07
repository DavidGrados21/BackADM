from fastapi import APIRouter, HTTPException
from db.db import get_db
from models.schemas import PacienteActualizar

router = APIRouter()

@router.put("/pacientes/{dni_paciente}")
def actualizar_paciente(
    dni_paciente: str,
    paciente: PacienteActualizar
):
    db = None

    try:
        db = get_db()
        cursor = db.cursor()

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

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Paciente no encontrado"
            )

        db.commit()

        return {
            "mensaje": "Paciente actualizado correctamente"
        }

    except HTTPException:
        raise

    except Exception:
        if db:
            db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )

    finally:
        if db:
            db.close()