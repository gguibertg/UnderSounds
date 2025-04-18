from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

PCONN = "\033[95mCONN\033[0m:\t "
PCONN_ERR = "\033[96mCTRL\033[0m|\033[91mERROR\033[0m:\t "

# Aquí se conecta a la base de datos de MongoDB Atlas y se obtienen las colecciones necesarias.

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
                print(PCONN, "Conexión con MongoDB Atlas exitosa.")
                MongoConnector.mongo_initialized = True
        except ConnectionFailure:
            print(PCONN_ERR, "No se pudo conectar con MongoDB.")
            self.db = None

    def get_db(self):
        print(PCONN, "Descargando base de datos...")
        if self.db is None:
            print(PCONN_ERR, "Database connection is not initialized.")
        return self.db
    
    def get_usuario_collection(self):
        print(PCONN, "Descargando usuarios...")
        if self.db is None:
            print(PCONN_ERR, "Database connection is not initialized.")
        return self.db.Usuarios

    def post_faq_collection(self):
        print("GET FAQS COLLECTION")
        if self.db is None:
            print(PCONN_ERR,"Database connection is not initialized.")
        return self.db.Preguntas
