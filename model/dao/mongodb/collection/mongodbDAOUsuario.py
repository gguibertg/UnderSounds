from ...intefaceUsuarioDAO import InterfaceUsuarioDAO
from ....dto.usuarioDTO import UsuarioDTO, UsuariosDTO

# Esta clase es una implementación de la interfaz InterfaceSongDAO para interactuar con MongoDB.
class mongodbUsuarioDAO(InterfaceUsuarioDAO):

    # En el constructor de la clase, se recibe la colección de MongoDB que se va a usar para interactuar con la base de datos.
    def __init__(self, collection):
        self.collection = collection
    
    def get_all_usuarios(self):
        users = UsuariosDTO()

        try:
            query = self.collection.find()

            # doc ya es un diccionario en MongoDB.
            for doc in query:
                user_dto = UsuarioDTO()
                user_dto.set_id(str(doc.get("_id")))
                user_dto.set_url(doc.get("url"))
                user_dto.set_nombre(doc.get("nombre"))
                user_dto.set_email(doc.get("email"))
                user_dto.set_bio(doc.get("bio"))
                user_dto.set_esArtista(doc.get("esArtista"))
                user_dto.set_imagen(doc.get("imagen"))

                users.insertUser(user_dto)

        except Exception as e:
            print(f"Error retrieving Users: {e}")

        return [user.usuario_to_dict() for user in users.userlist]
    