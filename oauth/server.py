from fastapi import FastAPI, Request, Response, Depends
from fastapi.templating import Jinja2Templates
import firebase_admin
from firebase_admin import auth, credentials
import uuid
import json

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Inicializar Firebase
cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred)

# Almacenamiento en memoria para sesiones
sessions = {}

#Simulación de datos de usuarios
user_data = {}

# Cargar datos desde JSON
with open("bd.json", "r", encoding="utf-8") as f:
    user_data = json.load(f)

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/login")
async def login(data: dict, response: Response, provider: str):
    print("LLEGO")
    token = data.get("token")
    try:
        decoded_token = auth.verify_id_token(token)
        # Identificador único del usuario otorgado por Firebase
        # que podemos usar como identificador del usuario en nuestra base de datos
        print(decoded_token)
        user_id = decoded_token["uid"]
        #print(user_id)
        #print(provider)
        session_id = str(uuid.uuid4())
        #Faltaría asignar vigencia a la sesión
        sessions[session_id] = {"user_id": user_id, "type": provider}
        response.set_cookie(key="session_id", value=session_id, httponly=True)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/login-credentials")
async def login_google(data: dict, response: Response):
    return await login(data, response, "credentials")

@app.post("/login-google")
async def login_google(data: dict, response: Response):
    return await login(data, response, "google")

@app.get("/perfil")
async def perfil(request: Request):
    print("PERFIL")
    session_id = request.cookies.get("session_id")
    #Faltaría comprobar la vigencia a la sesión
    if session_id in sessions:
        user_id = sessions[session_id]["user_id"]
        print(user_id)
        user_info = user_data["usuarios"].get(user_id)
        if user_info:
            return templates.TemplateResponse("profile.html", {"request": request, "user": user_info})
    return Response("No autorizado", status_code=401)

@app.post("/logout")
async def logout(request: Request, response: Response):
    session_id = request.cookies.get("session_id")
    print("CERRANDO SESSION:", session_id)
    if session_id in sessions:
        del sessions[session_id]
    response.delete_cookie("session_id")
    return {"success": True}


# Ejecución de la aplicación
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000, reload=True)