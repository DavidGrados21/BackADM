from fastapi import APIRouter
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import httpx
import os
import logging

load_dotenv()

router = APIRouter()

logger = logging.getLogger(__name__)

TOKEN_APIINTI = os.getenv("TOKEN_APIINTI")

@router.get("/consultar-dni/{dni}")
async def consultar_dni(dni: str):

    # =========================
    # VALIDAR DNI
    # =========================
    if not dni.isdigit() or len(dni) != 8:

        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "DNI inválido"
            }
        )

    async with httpx.AsyncClient(timeout=10) as client:

        # =========================
        # 1. GRAPH PERU
        # =========================
        try:

            response = await client.get(
                f"https://graphperu.daustinn.com/api/query/{dni}"
            )

            if response.status_code == 200:

                data = response.json()

                logger.info(f"GRAPH: {data}")

                if data.get("names") and data.get("surnames"):

                    nombre = " ".join([
                        data.get("names", ""),
                        data.get("surnames", "")
                    ]).strip()

                    return {
                        "success": True,
                        "nombre": nombre,
                        "source": "graphperu"
                    }

        except Exception as e:

            logger.error(f"Graph Perú error: {e}")

        # =========================
        # 2. APIINTI
        # =========================
        try:

            response = await client.get(
                f"https://app.apiinti.dev/api/v1/dni/{dni}",
                headers={
                    "Authorization": f"Bearer {TOKEN_APIINTI}",
                    "Accept": "application/json"
                }
            )

            if response.status_code == 200:

                data = response.json()

                logger.info(f"APIINTI: {data}")

                if data.get("success"):

                    d = data["data"]

                    nombre = " ".join([
                        d.get("nombres", ""),
                        d.get("apellidoPaterno", ""),
                        d.get("apellidoMaterno", "")
                    ]).strip()

                    return {
                        "success": True,
                        "nombre": nombre,
                        "source": "apiinti"
                    }

        except Exception as e:

            logger.error(f"ApiInti error: {e}")

    # =========================
    # NO ENCONTRADO
    # =========================
    return {
        "success": False,
        "message": "No se encontró información"
    }