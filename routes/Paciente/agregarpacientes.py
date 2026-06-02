from fastapi import APIRouter, HTTPException
from db.db import get_db
from models.schemas import PacienteCrear
from datetime import datetime

router = APIRouter()

@router.post("/pacientes")
def crear_paciente(paciente: PacienteCrear):
    db = get_db()
    cursor = db.cursor()

    try:
        fecha_nacimiento = None

        if paciente.fecha_nacimiento:
            fecha_nacimiento = datetime.strptime(
                paciente.fecha_nacimiento,
                "%d/%m/%Y"
            ).date()

        cursor.execute("""
            INSERT OR IGNORE INTO paciente (
                dni_paciente,
                nombre_paciente,
                sexo_paciente,
                fecha_nacimiento_paciente
            )
            VALUES (?, ?, ?, ?)
        """, (
            paciente.dni,
            paciente.nombre,
            paciente.sexo,
            fecha_nacimiento
        ))

        cursor.execute("""
            SELECT ce.id
            FROM casos_emergencia ce
            WHERE ce.dni_paciente = ?
        """, ( paciente.dni,))

        caso_existente = cursor.fetchone()
        
        if caso_existente:
            return {
                "mensaje": "El paciente ya está en cola",
                "dni_paciente": paciente.dni,
                "caso_id": caso_existente["id"]
            }

        # crear caso emergencia
        cursor.execute("""
            INSERT INTO casos_emergencia (
                dni_paciente,
                id_doctor,
                id_estado,
                prioridad,
                id_especialidad,
                origen
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            paciente.dni,
            1,
            1,
            5,
            1,
            paciente.origen
        ))

        caso_id = cursor.lastrowid

        # crear triaje inicial
        cursor.execute("""
            INSERT INTO triaje (
                caso_id,
                prioridad_ia
            )
            VALUES (?, ?)
        """, (
            caso_id,
            5
        ))

        db.commit()

        return {
            "mensaje": "Paciente registrado, en cola y listo para triaje",
            "paciente_id": paciente.dni,
            "caso_id": caso_id
        }

    except Exception as e:
        db.rollback()
        
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        db.close()