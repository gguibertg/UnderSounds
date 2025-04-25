from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

PCONN = "\033[95mCONN\033[0m:\t "
PCONN_ERR = "\033[96mCTRL\033[0m|\033[91mERROR\033[0m:\t "

class MongoConnector:
    mongo_initialized = False

    # Singleton pattern to ensure only one instance of MongoClient
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
    
    # User
    def get_usuario_collection(self):
        print(PCONN, "Descargando usuarios...")
        if self.db is None:
            print(PCONN_ERR, "Database connection is not initialized.")
        return self.db.Usuarios

    #Faqs
    def post_faq_collection(self):
        print(PCONN, "Descargando faqs...")
        if self.db is None:
            print(PCONN_ERR,"Database connection is not initialized.")
        return self.db.Preguntas
    
    # Album
    def get_album_collection(self):
        print(PCONN, "Descargando albumes...")
        if self.db is None:
            print(PCONN_ERR, "Database connection is not initialized.")
        return self.db.Albums
    
    # Genero
    def get_genero_collection(self):
        print(PCONN, "Descargando generos...")
        if self.db is None:
            print(PCONN_ERR, "Database connection is not initialized.")
        return self.db.Géneros
    
    # Cancion
    def post_song_collection(self):
        print(PCONN, "Descargando canciones...")
        if self.db is None:
            print(PCONN_ERR, "Database connection is not initialized.")
        return self.db.Cancion    
    
    # Carrito
    def get_articulos_carrito(self):
        print(PCONN, "Descargando artículos del carrito...")
        if self.db is None:
            print("Database connection is not initialized.")
            return []
        return self.db["Carrito"]
    
    # Contacto
    def get_contacto_collection(self):
        print(PCONN, "Descargando contacto...")
        if self.db is None:
            print(PCONN_ERR, "Database connection is not initialized.")
        return self.db.ContactoMsg
    
    # Reseña
    def get_reseña_collection(self):
        print(PCONN, "Descargando reseñas...")
        if self.db is None:
            print(PCONN_ERR, "Database connection is not initialized.")
        return self.db.Reseñas