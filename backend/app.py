from google import genai
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sesiones_de_chat = {}

class Consulta(BaseModel):
    usuario_id: str
    pregunta: str

INSTRUCCIONES_NEGOCIO = """
Eres el asistente experto de 'MundoMotero', un concesionario de motos premium.
Tu objetivo es vender y asesorar.
Reglas:
- Tus respuestas deben ser BREVES (máximo 2 o 3 frases).
- Termina casi siempre con una pregunta clara y específica para avanzar en la venta.
- Sé amable, entusiasta y usa términos moteros (cilindrada, torque, frenos ABS, caballos).
- Si preguntan por precios, diles que varían según el financiamiento y pídeles su número para contactarlos.
- No hables de carros, solo motos.
- Si no sabes algo, invita al cliente a visitar el concesionario físico.
"""


@app.post('/chatBot')
async def chatBot_gemini(consulta: Consulta):
    uid = consulta.usuario_id

    if uid not in sesiones_de_chat:
        sesiones_de_chat[uid] = client.chats.create(
            model="gemini-2.5-flash",
            config={
                "system_instruction": INSTRUCCIONES_NEGOCIO
            }
        )

    response = sesiones_de_chat[uid].send_message(consulta.pregunta)

    return {
        "usuario_id": uid,
        "remitente": "bot",
        "respuesta": response.text
    }