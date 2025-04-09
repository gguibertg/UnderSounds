from fastapi import FastAPI, status, HTTPException
from model.dao.mongodb.database import db
from model.dto.usuarios_dto import Usuario

app = FastAPI()

@app.post("/userdb", response_model=Usuario, status_code=status.HTTP_201_CREATED)
async def user (user: Usuario):
    if type(search_user(user.email)) == Usuario:
        raise HTTPException( status_code=status.HTTP_404_NOT_FOUND, details="El usuario introducido ya existe")
    
    user_dict = dict(user)
    del user_dict["id"]

    id = db.Usuarios.insert_one(user_dict).inserted_id

    new_user = user_schema(db.Usuarios.find_one({"_id": id}))

    return Usuario(**new_user)


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