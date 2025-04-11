from ...intefaceDAOUsuario import InterfaceUsuarioDAO

# Esta clase es una implementación de la interfaz InterfaceSongDAO para interactuar con MongoDB.
class mongodbUsuarioDAO(InterfaceUsuarioDAO):

    # En el constructor de la clase, se recibe la colección de MongoDB que se va a usar para interactuar con la base de datos.
    def __init__(self, collection):
        self.collection = collection
    
    # Definimos un método que se va a usar para obtener las canciones de la base de datos.
    # Este método estaba definido como abstracto en la interfaz InterfaceSongDAO, como podréis recordar.
    def getAllUsuarios(self):
        try:
            query = self.collection # (Local)
        except Exception as e:
            print(e)
        
        return query

    def getUsuario(self, email):
        try:
            query = self.collection # (Local)
        except Exception as e:
            print(e)
        
        return query
    