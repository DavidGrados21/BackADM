from fastapi import APIRouter, HTTPException
from db.db import get_db
from models.schemas import PacienteActualizar

router = APIRouter()

@router.put("/pacientes/{paciente_id}")
def actualizar_paciente(
    paciente_id: int,
    paciente: PacienteActualizar
):
    db = get_db()
    cursor = db.cursor()

    try:
        # verificar si existe
        cursor.execute("""
            SELECT id
            FROM pacientes
            WHERE id = ?
        """, (paciente_id,))

        existe = cursor.fetchone()

        if not existe:
            raise HTTPException(
                status_code=404,
                detail="Paciente no encontrado"
            )

        cursor.execute("""
            UPDATE pacientes
            SET
                telefono = ?,
                direccion = ?,
                tipo_sangre = ?,
                tiene_tatuajes = ?,
                religion = ?,
                contacto_emergencia = ?
            WHERE id = ?
        """, (
            paciente.telefono,
            paciente.direccion,
            paciente.tipo_sangre,
            paciente.tiene_tatuajes,
            paciente.religion,
            paciente.contacto_emergencia,
            paciente_id
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