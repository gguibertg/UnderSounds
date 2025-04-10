from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

class MongoConnector:
    mongo_initialized = False

    def __init__(self):
        try:
            if not MongoConnector.mongo_initialized:
                self.client = MongoClient(
                    "mongodb+srv://cliente:PIL1G4@piproyect.anlag1u.mongodb.net/?retryWrites=true&w=majority&appName=PIProyect",
                    serverSelectionTimeoutMS=3000
                )
                self.client.admin.command("ping")  # Verifica la conexión
                self.db = self.client["UnderSoundsData"]
                print("Conexión con MongoDB Atlas exitosa.")
                MongoConnector.mongo_initialized = True
        except ConnectionFailure:
            print("No se pudo conectar con MongoDB.")
            self.db = None

    def get_db(self):
        if self.db is None:
            print("Database connection is not initialized.")
        return self.db

    def get_faq_collection(self):
        print("GET FAQS COLLECTION")
        if self.db is None:
            print("Database connection is not initialized.")
        return self.db["Preguntas"]
