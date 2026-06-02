from fastapi import APIRouter, HTTPException
from db.db import get_db

router = APIRouter(prefix="/doctor",tags=["Doctor"])

ESTADOS = {
    "entrante": 1,
    "pendiente": 2,
    "en_atencion": 3,
    "finalizado": 4
}

@router.get("/{id_doctor}/casos/{estado}")
def obtener_casos_doctor_estado(id_doctor: int, estado: str):
    db = get_db()
    cursor = db.cursor()

    try:
        estado = estado.lower()

        if estado not in ESTADOS:
            raise HTTPException(
                status_code=404,
                detail="Estado no válido"
            )

        id_estado = ESTADOS[estado]

        cursor.execute("""
            SELECT
                ce.id AS caso_id,
                p.nombre_paciente AS nombre,
                p.dni_paciente AS dni,
                ce.prioridad,
                ce.fecha_llegada
            FROM casos_emergencia ce
            JOIN paciente p
                ON p.dni_paciente = ce.dni_paciente
            WHERE ce.id_doctor = ?
              AND ce.id_estado = ?
            ORDER BY
                ce.prioridad ASC,
                ce.fecha_llegada ASC
        """, (id_doctor, id_estado))

        rows = cursor.fetchall()

        casos = [
            {
                "caso_id": r["caso_id"],
                "dni": r["dni"],
                "nombre": r["nombre"],
                "prioridad": r["prioridad"],
                "fecha_llegada": r["fecha_llegada"]
            }
            for r in rows
        ]

        return {
            "casos": casos
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        db.close()