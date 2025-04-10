from ...interfaceSongDAO import InterfaceSongDAO

class MongodbSongDAO(InterfaceSongDAO):
    def __init__(self, collection=None):
        self.collection = collection

    def get_all_songs(self):
        # Devuelve una lista vacía por ahora
        return []