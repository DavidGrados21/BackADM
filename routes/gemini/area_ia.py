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

@router.post("/clasificar-area")
def clasificar_paciente(datos: PacienteSintomas):
    try:
        instrucciones_sistema = (
            "Eres un clasificador de derivación médica. "
            "Debes devolver exactamente una de las siguientes etiquetas: "
            "PEDIATRIA, MATERNIDAD, CIRUGIA, TRAUMATOLOGIA, MEDICINA GENERAL.\n\n"
            "Reglas:\n"
            "- PEDIATRIA: pacientes menores de 15 años o patologías pediátricas.\n"
            "- MATERNIDAD: embarazo, controles prenatales, trabajo de parto, puerperio y complicaciones obstétricas.\n"
            "- CIRUGIA: patologías que puedan requerir evaluación o intervención quirúrgica.\n"
            "- TRAUMATOLOGIA: fracturas, golpes, caídas, esguinces, luxaciones, dolor osteomuscular o lesiones traumáticas.\n"
            "- MEDICINA GENERAL: cualquier otro motivo de consulta.\n\n"
            "Salida obligatoria: devuelve únicamente una etiqueta exacta de la lista anterior."
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
            area = response.text.strip()
        else:

            raise HTTPException(status_code=400, detail="La IA no pudo generar una prioridad para estos síntomas.")

        return {"area": area}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la IA: {str(e)}")