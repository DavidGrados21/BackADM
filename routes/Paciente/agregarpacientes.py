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
        # convertir fecha dd/mm/yyyy -> yyyy-mm-dd
        fecha_nacimiento = None

        if paciente.fecha_nacimiento:
            fecha_nacimiento = datetime.strptime(
                paciente.fecha_nacimiento,
                "%d/%m/%Y"
            ).date()

        cursor.execute("""
            INSERT OR IGNORE INTO pacientes 
            (dni, nombre, sexo, fecha_nacimiento)
            VALUES (?, ?, ?, ?)
        """, (
            paciente.dni,
            paciente.nombre,
            paciente.sexo,
            fecha_nacimiento
        ))

        cursor.execute(
            "SELECT id FROM pacientes WHERE dni = ?",
            (paciente.dni,)
        )

        row = cursor.fetchone()

        if not row:
            raise HTTPException(500, "Error al obtener paciente")

        paciente_id = row["id"]

        # verificar caso activo
        cursor.execute("""
            SELECT id FROM casos_emergencia 
            WHERE paciente_id = ? AND estado_id != 4
        """, (paciente_id,))

        caso_existente = cursor.fetchone()

        if caso_existente:
            return {
                "mensaje": "El paciente ya está en cola",
                "paciente_id": paciente_id,
                "caso_id": caso_existente["id"]
            }

        # crear caso emergencia
        cursor.execute("""
            INSERT INTO casos_emergencia 
            (paciente_id, estado_id, prioridad, origen)
            VALUES (?, 1, 5, ?)
        """, (paciente_id,
              paciente.origen,
              ))

        caso_id = cursor.lastrowid

        # crear triaje inicial
        cursor.execute("""
            INSERT INTO triaje (caso_id, prioridad_ia)
            VALUES (?, ?)
        """, (caso_id, 5))

        db.commit()

        return {
            "mensaje": "Paciente registrado, en cola y listo para triaje",
            "paciente_id": paciente_id,
            "caso_id": caso_id
        }

    except Exception as e:
        db.rollback()
        print("ERROR crear_paciente:", e)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        db.close()