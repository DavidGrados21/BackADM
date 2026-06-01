from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types
import os

load_dotenv()

TOKEN_GEMINI = os.getenv("TOKEN_GEMINI")
router = APIRouter( prefix="/triaje", tags=["Triaje Inteligente"])
client = genai.Client(api_key= TOKEN_GEMINI )
class PacienteSintomas(BaseModel):
    sintomas: str

@router.post("/clasificar-doctor")
def clasificar_paciente(datos: PacienteSintomas):
    try:
        instrucciones_sistema = (
            "Actúas como un sistema de derivación médica hospitalaria. "
            "Analiza los síntomas y selecciona únicamente una de las siguientes especialidades: "
            "CARDIOLOGIA,NEUROLOGIA,TRAUMATOLOGIA PEDIATRICA,GASTROENTEROLOGIA,OFTALMOLOGIA. "
            "Responde únicamente con una de esas categorías. "
            "No agregues explicaciones ni texto adicional."
        )

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=datos.sintomas,
            config=types.GenerateContentConfig(
                system_instruction=instrucciones_sistema,
                temperature=0.1
            )
        )

        if response.text:
            especialidadM = response.text.strip()
        else:

            raise HTTPException(status_code=400, detail="La IA no pudo generar una prioridad para estos síntomas.")

        return {"especialidad": especialidadM}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la IA: {str(e)}")