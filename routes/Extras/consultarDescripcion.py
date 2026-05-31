from fastapi import APIRouter, HTTPException
from db.db import get_db

router = APIRouter()

@router.get("/descripcion/{caso_id}")
def obtener_descripcion(caso_id: int):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT sintomas FROM triaje WHERE caso_id = ?",
        (caso_id,)
    )

    resultado = cursor.fetchone()
    conn.close()

    if not resultado:
        raise HTTPException(status_code=404, detail="Triaje no encontrado")

    return {
        "caso_id": caso_id,
        "sintomas": resultado[0]
    }