from ...intefaceGeneroDAO import InterfaceGeneroDAO
from ....dto.generoDTO import GeneroDTO, GenerosDTO

PDAO = "\033[95mDAO\033[0m:\t "
PDAO_ERROR = "\033[96mDAO\033[0m|\033[91mERROR\033[0m:\t "

# Esta clase implementa los métodos que se usaran en las llamadas del Model.
# En concreto, esta es la clase destinada para lo relacionado con la colección de Usuarios en MongoDB.
class mongodbGeneroDAO(InterfaceGeneroDAO):

    # En el constructor de la clase, se recibe la colección de MongoDB que se va a usar para interactuar con la base de datos.
    def __init__(self, collection):
        self.collection = collection

    def get_genero(self, id):
        genero = None

        try:
            query = self.collection.find_one({"_id": id})

            if query:
                genero = GeneroDTO()
                genero.set_id(query.get("_id"))
                genero.set_nombre(query.get("nombre"))
                genero.set_esSubGen(query.get("esSubGen"))
                
        except Exception as e:
            print(f"{PDAO_ERROR}Error al recuperar el género: {e}")

        return genero.genero_to_dict() if genero else None

    def get_generos(self):
        generos = GenerosDTO()

        try:
            query = self.collection.find()

            # doc ya es un diccionario en MongoDB.
            for doc in query:
                genero = GeneroDTO()
                genero.set_id(str (doc.get("_id")))
                genero.set_nombre(doc.get("nombre"))
                genero.set_esSubGen(doc.get("esSubGen"))
                generos.insertGenero(genero)

        except Exception as e:
            print(f"Error al recuperar los Generos: {e}")
            
        return [genero.genero_to_dict() for genero in generos.generolist]