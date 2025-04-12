import pymongo
import pymongo.results
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


    def get_usuario(self, id):
        user = None

        try:
            query = self.collection.find_one({"_id": id})

            if query:
                user = UsuarioDTO()
                user.set_id(str(query.get("_id")))
                user.set_url(query.get("url"))
                user.set_nombre(query.get("nombre"))
                user.set_email(query.get("email"))
                user.set_bio(query.get("bio"))
                user.set_esArtista(query.get("esArtista"))
                user.set_imagen(query.get("imagen"))

        except Exception as e:
            print(f"Error retrieving User: {e}")

        return user.usuario_to_dict() if user else None
    

    def add_usuario(self, usuario) -> bool:
        try:
            user_dict : dict = usuario.usuario_to_dict()
            user_dict["_id"] = user_dict.pop("id", None)
            result : pymongo.results.InsertOneResult = self.collection.insert_one(user_dict)
            return result.inserted_id == user_dict["_id"]
        
        except Exception as e:
            print(f"Error adding User: {e}")
            return False
        

    def update_usuario(self, usuario) -> bool:
        try:
            user_dict : dict = usuario.usuario_to_dict()
            user_dict["_id"] = user_dict.pop("id", None)
            result : pymongo.results.UpdateResult = self.collection.update_one({"_id": user_dict["_id"]}, {"$set": user_dict})
            return result.modified_count == 1
        
        except Exception as e:
            print(f"Error updating User: {e}")
            return False
    

    def delete_usuario(self, id) -> bool:
        try:
            result : pymongo.results.DeleteResult = self.collection.delete_one({"_id": id})
            return result.deleted_count == 1
        
        except Exception as e:
            print(f"Error deleting User: {e}")
            return False