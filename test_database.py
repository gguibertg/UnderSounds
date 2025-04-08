from fastapi import FastAPI
from model.dao.mongodb.database import db
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
import os

# Carga de variables desde archivo .env (opcional)
load_dotenv()

app = FastAPI()

# Verificar la conexión al iniciar la app
@app.on_event("startup")
def verificar_conexion():
    global db, conexion_exitosa
    try:
        conexion_exitosa = True
        print("✅ Conectado correctamente a MongoDB")
    except ConnectionFailure as e:
        conexion_exitosa = False
        db = None
        print("❌ Fallo de conexión con MongoDB:", e)

# Ruta de prueba para verificar conexión
@app.get("/test-db")
def test_db():
    if conexion_exitosa:
        return {"estado": "ok", "mensaje": f"Conexión a '{db}' exitosa"}
    else:
        return {"estado": "error", "mensaje": "No se pudo conectar a MongoDB"}