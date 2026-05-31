from fastapi import FastAPI
from contextlib import asynccontextmanager
from db.db import init_db
from db.seed import seed_data
from routes import mostrarcola, triaje
from routes.Extras import paseaatencion,consultadni

from fastapi.middleware.cors import CORSMiddleware

from routes.Paciente import agregarpacientes,editarpaciente,mostrarpaciente,mostrarpacientes
from routes.gemini import gemini

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🔹 Startup
    init_db()
    seed_data()
    print("✅ Base de datos inicializada")

    yield

    # 🔹 Shutdown (opcional)
    print("🛑 Cerrando aplicación")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agregarpacientes.router)
app.include_router(editarpaciente.router)
app.include_router(mostrarpaciente.router)
app.include_router(mostrarpacientes.router)

app.include_router(triaje.router)
app.include_router(mostrarcola.router)
app.include_router(paseaatencion.router)
app.include_router(consultadni.router)

app.include_router(gemini.router)