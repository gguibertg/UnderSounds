from ...interfaceDAOSong import InterfaceSongDAO

# Esta clase es una implementación de la interfaz InterfaceSongDAO para interactuar con MongoDB.
class MongoDBSongDAO(InterfaceSongDAO):

    # En el constructor de la clase, se recibe la colección de MongoDB que se va a usar para interactuar con la base de datos.
    def __init__(self, collection):
        self.collection = collection
    
    # Definimos un método que se va a usar para obtener las canciones de la base de datos.
    # Este método estaba definido como abstracto en la interfaz InterfaceSongDAO, como podréis recordar.
    def get_songs(self):
        try:
#             #query = self.collection.stream() # (Firebase)
            query = self.collection # (Local)
#             print(query)
        except Exception as e:
            print(e)
        
        return query
    

    # Continuamos añadiendo implementaciones de las abstract methods de la interfaz InterfaceSongDAO...