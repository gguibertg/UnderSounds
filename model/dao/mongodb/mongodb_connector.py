from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

try:
    client = MongoClient("mongodb+srv://cliente:PIL1G4@piproyect.anlag1u.mongodb.net/?retryWrites=true&w=majority&appName=PIProyect", serverSelectionTimeoutMS=3000)
    client.admin.command("ping")  # Lanzamos ping al servidor
    print("El cliente se ha conectado a MongoDB correctamente")
    db = client["UnderSoundsData"]
except ConnectionFailure:
    print("El cliente no se pudo conectar a MongoDB")
    db = None