from ...factory.interface_dao_factory import InterfaceDAOFactory
from .collection.mongodbDAOSong import mongodbSongDAO
#from firebase_admin import credentials, firestore, initialize_app, auth

# -----------------------------------------------------------
# No se muy bien para que sirve esta clase.
# Quien lo sepa mejor, que lo explique aquí:
# -----------------------------------------------------------

class mongodbDAOFactory(InterfaceDAOFactory):

    def __init__(self):
#         ## Conexion bd 
        self.db = {"songs" : [
         {'album': 'A Night at the Opera', 'author': 'Queen', 'id': 'EGDjQKq3kMroVWapLhoG', 'duration': '5:55', 'musicgenre': 'Rock', 'price': 1.99, 'rating': 5, 'release': '1975-10-30 23:00:00.215000+00:00', 'title': 'Bohemian Rhapsody'}, 
          {'album': 'Thriller', 'author': 'Michael Jackson', 'id': 'MuT75L6x43aWumwAEwYc', 'duration': 0, 'musicgenre': 'Pop', 'price': 1.99, 'rating': '5', 'release': '1983-01-01 23:00:00.408000+00:00', 'title': 'Billie Jean'}
         ]
         } # (Local)
#         """
#         Código para la conexión con firebase
#         try:
#             self.credentials = credentials.Certificate("model//dao//firebase//credentials.json")
#             initialize_app(self.credentials)
#             self.db = firestore.client()
#             print("Connection to Firebase Firestore initialized successfully.")
#         except Exception as e:
#             print("Error in connecting with db")
#             print(e)
#         """
    def getSongDao(self):
#         # collection = self.db.collection("songs") (Firebase)
        collection = self.db["songs"] # (Local)
        return mongodbSongDAO(collection)