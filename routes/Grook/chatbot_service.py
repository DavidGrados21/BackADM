from groq import Groq
import os

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def generate_response(message: str):

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """
                Eres SITEC, un asistente virtual de orientación en salud.
                
                REGLAS:
                - No te presentes.
                - No saludes.
                - Responde directamente a la consulta.
                - Máximo 2 frases cortas.
                - Máximo 60 palabras.
                - No diagnostiques enfermedades.
                - No recetes medicamentos.
                - No indiques dosis.
                - Brinda orientación general.

                Si detectas síntomas potencialmente graves,
                recomienda atención médica profesional de forma breve.
                """
            },
            {
                "role": "user",
                "content": message
            }
        ],
        temperature=0.3,
        max_tokens=100
    )

    return completion.choices[0].message.content