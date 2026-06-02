from fastapi import APIRouter, HTTPException
from db.db import get_db

router = APIRouter()

@router.get("/cola/{estado}")
def obtener_por_estado(estado: str):
    db = get_db()
    cursor = db.cursor()

    try:
        estado = estado.lower()

        if estado not in ESTADOS:
            raise HTTPException(404, "Estado no válido")

        id_estado = ESTADOS[estado]

        cursor.execute("""
            SELECT
                ce.id AS caso_id,
                p.nombre_paciente AS nombre,
                p.dni_paciente AS dni,
                ce.prioridad,
                ce.fecha_llegada,
                ce.id_estado
            FROM casos_emergencia ce
            
            JOIN paciente p ON p.dni_paciente = ce.dni_paciente
            
            WHERE ce.id_estado = ?
            
            ORDER BY
                ce.prioridad ASC,
                ce.fecha_llegada ASC
                
        """, (id_estado,))

        rows = cursor.fetchall()

        resultado = []

        for r in rows:
            item = {
                "caso_id": r["caso_id"],
                "dni": r["dni"],
                "nombre": r["nombre"],
                "id_estado": r["id_estado"]
            }

            if estado in ["pendiente", "en_atencion"]:
                item["prioridad"] = r["prioridad"]

            resultado.append(item)

        return {
            "estado": estado,
            "total": len(resultado),
            "casos": resultado
        }

    except HTTPException:
        raise
    
    except Exception as e:
        print("ERROR obtener_por_estado:", e)
        raise HTTPException(status_code=500,detail=str(e))
    
    finally:
        db.close()

ESTADOS = {
    "entrante": 1,
    "pendiente": 2,
    "en_atencion": 3,
    "finalizado": 4
}