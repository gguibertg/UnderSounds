from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from ...factory.interface_dao_factory import InterfaceDAOFactory
from .collection.mongodbDAOSong import mongodbSongDAO
#from firebase_admin import credentials, firestore, initialize_app, auth

# -----------------------------------------------------------
# Clase para inicializar la Base de Datos con MongoDB
# -----------------------------------------------------------

class mongodbDAOFactory(InterfaceDAOFactory):

    def __init__(self):
        try:
            client = MongoClient("mongodb+srv://cliente:PIL1G4@piproyect.anlag1u.mongodb.net/?retryWrites=true&w=majority&appName=PIProyect", serverSelectionTimeoutMS=3000)
            client.admin.command("ping")  # Lanzamos ping al servidor
            print("El cliente se ha conectado a MongoDB correctamente")
            self.db = client["UnderSoundsData"]
        except ConnectionFailure:
            print("El cliente no se pudo conectar a MongoDB")
            self.db = None


    def getSongDao(self):
#         # collection = self.db.collection("songs") (Firebase)
        collection = self.db.Cancion # (Local)
        return mongodbSongDAO(collection)