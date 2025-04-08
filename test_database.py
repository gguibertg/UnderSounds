from fastapi import FastAPI, status, HTTPException
from model.dao.mongodb.database import db
from model.dto.usuarios_dto import Usuario
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
        return {"estado": "ok", "mensaje": f"Conexión a '{db.name}' exitosa"}
    else:
        return {"estado": "error", "mensaje": "No se pudo conectar a MongoDB"}

@app.post("/user-db", response_model=Usuario, status_code=status.HTTP_201_CREATED)
async def user (user: Usuario):
    try:
        if type(search_user(user.email)) == Usuario:
            raise HTTPException( status_code=status.HTTP_404_NOT_FOUND, details="El usuario introducido ya existe")
        
        user_dict = dict(user)
        del user_dict["id"]

        id = db.Usuarios.insert_one(user_dict).inserted_id

        new_user = user_schema(db.Usuarios.find_one({"_id": id}))

        return Usuario(**new_user)
    except Exception as e:
        return {"error": str(e)}


def search_user(email: str):
    try:
        user = db.Usuarios.find_one({"email": email})
        return Usuario(**user_schema(user))
    
    except:
        return {"error": "No se ha encontrado el usuario"}


def user_schema(user) -> dict:
    return {
            "id": str(user["_id"]),
            "bio": user["bio"],
            "email": user["email"],
            "contraseña": user["contraseña"],
            "imagen": user["imagen"],
            "url": user["url"],
            "nombre": user["nombre"],
            "telefono": user["telefono"]
            }