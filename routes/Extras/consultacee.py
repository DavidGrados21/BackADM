from fastapi import APIRouter
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import httpx
import os
import logging

load_dotenv()

router = APIRouter()

logger = logging.getLogger(__name__)

TOKEN_JSON_PE = os.getenv("TOKEN_JSON_PE")

TOKEN_JSON_PE = os.getenv("TOKEN_JSON_PE")

@router.get("/consultar-cee/{cee}")
async def consultar_cee(cee: str):

    if not cee.isdigit():

        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "Carné de extranjería inválido"
            }
        )

    async with httpx.AsyncClient(timeout=10) as client:

        try:

            response = await client.post(
                "https://api.json.pe/api/ce",
                headers={
                    "Authorization": f"Bearer {TOKEN_JSON_PE}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                json={
                    "ce": cee
                }
            )

            if response.status_code == 200:

                data = response.json()

                logger.info(f"JSON.PE CE: {data}")

                if data.get("success"):

                    d = data["data"]

                    nombre = " ".join([
                        d.get("nombres", ""),
                        d.get("apellido_paterno", ""),
                        d.get("apellido_materno", "")
                    ]).strip()

                    return {
                        "success": True,
                        "nombre": nombre,
                        "source": "jsonpe"
                    }

        except Exception as e:

            logger.error(f"JSON.PE error: {e}")

    return {
        "success": False,
        "message": "No se encontró información"
    }