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


@router.post("/clasificar-triaje")
def clasificar_paciente(datos: PacienteSintomas):
    try:
        instrucciones_sistema = (
            "Eres un enfermero experto en triaje clínico utilizando el Método ESI (Emergency Severity Index). "
            "Te proporcionaré los síntomas de un paciente y tu única tarea es determinar su nivel de prioridad. "
            "REGLA CRÍTICA DE SALIDA: Responde ÚNICAMENTE con el número correspondiente a la prioridad "
            "(un solo dígito del 1 al 5). No agregues texto antes ni después, no incluyas la palabra 'ESI', "
            "no saludes, no justifiques tu respuesta ni uses signos de puntuación. Solo devuelve el número."
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
            numero_prioridad = response.text.strip()
        else:

            raise HTTPException(status_code=400, detail="La IA no pudo generar una prioridad para estos síntomas.")

        return {"prioridad": numero_prioridad}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la IA: {str(e)}")