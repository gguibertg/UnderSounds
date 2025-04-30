import pymongo
import pymongo.results
from datetime import datetime, timedelta
from ...intefaceUsuarioDAO import InterfaceUsuarioDAO
from ....dto.usuarioDTO import UsuarioDTO, UsuariosDTO

PDAO = "\033[95mDAO\033[0m:\t "
PDAO_ERROR = "\033[96mDAO\033[0m|\033[91mERROR\033[0m:\t "

# Esta clase implementa los métodos que se usaran en las llamadas del Model.
# En concreto, esta es la clase destinada para lo relacionado con la colección de Usuarios en MongoDB.
class mongodbUsuarioDAO(InterfaceUsuarioDAO):

    # En el constructor de la clase, se recibe la colección de MongoDB que se va a usar para interactuar con la base de datos.
    def __init__(self, collection):
        self.collection = collection
    
    def get_all_usuarios_by_song(self, song_id):
        users = UsuariosDTO()
        try:
            query = self.collection.find({"biblioteca": song_id})

            for doc in query:
                user_dto = UsuarioDTO()
                user_dto.set_id(str(doc.get("_id")))
                user_dto.set_nombre(doc.get("nombre"))
                user_dto.set_bio(doc.get("bio"))
                user_dto.set_email(doc.get("email"))
                user_dto.set_imagen(doc.get("imagen"))
                user_dto.set_url(doc.get("url"))
                user_dto.set_fechaIngreso(doc.get("fechaIngreso"))
                user_dto.set_esArtista(doc.get("esArtista"))
                user_dto.set_esVisible(doc.get("esVisible"))
                user_dto.set_emailVisible(doc.get("emailVisible"))
                user_dto.set_id_likes(doc.get("id_likes", []))
                user_dto.set_studio_albumes(doc.get("studio_albumes", []))
                user_dto.set_studio_canciones(doc.get("studio_canciones", []))
                user_dto.set_biblioteca(doc.get("biblioteca", []))
                user_dto.set_listas_reproduccion(doc.get("listas_reproduccion", []))

                users.insertUser(user_dto)

        except Exception as e:
            print(f"{PDAO_ERROR}Error al recuperar los usuarios: {e}")

        return [user.usuario_to_dict() for user in users.userlist]
    
    def get_all_usuarios_by_song_in_list(self, song_id):
        users = UsuariosDTO()
        try:
            query = self.collection.find({"biblioteca": song_id})

            for doc in query:
                user_dto = UsuarioDTO()
                user_dto.set_id(str(doc.get("_id")))
                user_dto.set_nombre(doc.get("nombre"))
                user_dto.set_bio(doc.get("bio"))
                user_dto.set_email(doc.get("email"))
                user_dto.set_imagen(doc.get("imagen"))
                user_dto.set_url(doc.get("url"))
                user_dto.set_fechaIngreso(doc.get("fechaIngreso"))
                user_dto.set_esArtista(doc.get("esArtista"))
                user_dto.set_esVisible(doc.get("esVisible"))
                user_dto.set_emailVisible(doc.get("emailVisible"))
                user_dto.set_id_likes(doc.get("id_likes", []))
                user_dto.set_studio_albumes(doc.get("studio_albumes", []))
                user_dto.set_studio_canciones(doc.get("studio_canciones", []))
                user_dto.set_biblioteca(doc.get("biblioteca", []))
                user_dto.set_listas_reproduccion(doc.get("listas_reproduccion", []))

                users.insertUser(user_dto)

        except Exception as e:
            print(f"{PDAO_ERROR}Error al recuperar los usuarios: {e}")

        return [user.usuario_to_dict() for user in users.userlist]

    def get_all_by_fecha(self, fecha_str):
        users = UsuariosDTO()
        try:
            fecha_min = None
            fecha_max = None

            if len(fecha_str) == 4:  # Año: "2025"
                fecha_min = datetime.strptime(fecha_str, "%Y")
                fecha_max = datetime(fecha_min.year + 1, 1, 1)

            elif len(fecha_str) == 7:  # Año y mes: "2025-04"
                fecha_min = datetime.strptime(fecha_str, "%Y-%m")
                if fecha_min.month == 12:
                    fecha_max = datetime(fecha_min.year + 1, 1, 1)
                else:
                    fecha_max = datetime(fecha_min.year, fecha_min.month + 1, 1)

            elif len(fecha_str) == 10:  # Fecha completa: "2025-04-27"
                fecha_min = datetime.strptime(fecha_str, "%Y-%m-%d")
                fecha_max = fecha_min + timedelta(days=1)

            else:
                raise ValueError("Formato de fecha inválido")

            query = self.collection.find({
                "fechaIngreso": {
                    "$gte": fecha_min,
                    "$lt": fecha_max
                },
                "esArtista": True, 
                "esVisible": True
            })
            for doc in query:
                user_dto = UsuarioDTO()
                user_dto.set_id(str(doc.get("_id")))
                user_dto.set_nombre(doc.get("nombre"))
                user_dto.set_bio(doc.get("bio"))
                user_dto.set_email(doc.get("email"))
                user_dto.set_imagen(doc.get("imagen"))
                user_dto.set_url(doc.get("url"))
                user_dto.set_fechaIngreso(doc.get("fechaIngreso"))
                user_dto.set_esArtista(doc.get("esArtista"))
                user_dto.set_esVisible(doc.get("esVisible"))
                user_dto.set_emailVisible(doc.get("emailVisible"))
                user_dto.set_id_likes(doc.get("id_likes", []))
                user_dto.set_studio_albumes(doc.get("studio_albumes", []))
                user_dto.set_studio_canciones(doc.get("studio_canciones", []))
                user_dto.set_biblioteca(doc.get("biblioteca", []))
                user_dto.set_listas_reproduccion(doc.get("listas_reproduccion", []))

                users.insertUser(user_dto)

        except Exception as e:
            print(f"{PDAO_ERROR}Error al recuperar los usuarios: {e}")

        return [user.usuario_to_dict() for user in users.userlist]
    
    def get_all_by_nombre(self, nombre):
        users = UsuariosDTO()
        try:
            query = self.collection.find({"nombre": {"$regex": nombre, "$options": "i"}, "esArtista": True, "esVisible": True})

            for doc in query:
                user_dto = UsuarioDTO()
                user_dto.set_id(str(doc.get("_id")))
                user_dto.set_nombre(doc.get("nombre"))
                user_dto.set_bio(doc.get("bio"))
                user_dto.set_email(doc.get("email"))
                user_dto.set_imagen(doc.get("imagen"))
                user_dto.set_url(doc.get("url"))
                user_dto.set_fechaIngreso(doc.get("fechaIngreso"))
                user_dto.set_esArtista(doc.get("esArtista"))
                user_dto.set_esVisible(doc.get("esVisible"))
                user_dto.set_emailVisible(doc.get("emailVisible"))
                user_dto.set_id_likes(doc.get("id_likes", []))
                user_dto.set_studio_albumes(doc.get("studio_albumes", []))
                user_dto.set_studio_canciones(doc.get("studio_canciones", []))
                user_dto.set_biblioteca(doc.get("biblioteca", []))
                user_dto.set_listas_reproduccion(doc.get("listas_reproduccion", []))

                users.insertUser(user_dto)

        except Exception as e:
            print(f"{PDAO_ERROR}Error al recuperar los usuarios: {e}")

        return [user.usuario_to_dict() for user in users.userlist]

    def get_artistas(self):
        users = UsuariosDTO()
        try:
            query = self.collection.find({"esArtista": True, "esVisible": True})

            for doc in query:
                user_dto = UsuarioDTO()
                user_dto.set_id(str(doc.get("_id")))
                user_dto.set_nombre(doc.get("nombre"))
                user_dto.set_bio(doc.get("bio"))
                user_dto.set_email(doc.get("email"))
                user_dto.set_imagen(doc.get("imagen"))
                user_dto.set_url(doc.get("url"))
                user_dto.set_fechaIngreso(doc.get("fechaIngreso"))
                user_dto.set_esArtista(doc.get("esArtista"))
                user_dto.set_esVisible(doc.get("esVisible"))
                user_dto.set_emailVisible(doc.get("emailVisible"))
                user_dto.set_id_likes(doc.get("id_likes", []))
                user_dto.set_studio_albumes(doc.get("studio_albumes", []))
                user_dto.set_studio_canciones(doc.get("studio_canciones", []))
                user_dto.set_biblioteca(doc.get("biblioteca", []))
                user_dto.set_listas_reproduccion(doc.get("listas_reproduccion", []))

                users.insertUser(user_dto)

        except Exception as e:
            print(f"{PDAO_ERROR}Error al recuperar los artistas: {e}")

        return [user.usuario_to_dict() for user in users.userlist]

    def get_usuario(self, id):
        user = None

        try:
            query = self.collection.find_one({"_id": id})

            if query:
                user = UsuarioDTO()
                user.set_id(str(query.get("_id")))
                user.set_nombre(query.get("nombre"))
                user.set_bio(query.get("bio"))
                user.set_email(query.get("email"))
                user.set_imagen(query.get("imagen"))
                user.set_url(query.get("url"))
                user.set_fechaIngreso(query.get("fechaIngreso"))
                user.set_esArtista(query.get("esArtista"))
                user.set_esVisible(query.get("esVisible"))
                user.set_emailVisible(query.get("emailVisible"))
                user.set_studio_albumes(query.get("studio_albumes", []))
                user.set_studio_canciones(query.get("studio_canciones", []))
                user.set_id_likes(query.get("id_likes", []))
                user.set_biblioteca(query.get("biblioteca", []))
                user.set_listas_reproduccion(query.get("listas_reproduccion", []))

        except Exception as e:
            print(f"{PDAO_ERROR}Error al recuperar el usuario: {e}")

        return user.usuario_to_dict() if user else None
    
    def add_usuario(self, usuario : UsuarioDTO) -> bool:
        try:
            user_dict : dict = usuario.usuario_to_dict()
            user_dict["_id"] = user_dict.pop("id", None)
            result : pymongo.results.InsertOneResult = self.collection.insert_one(user_dict)
            return result.inserted_id == user_dict["_id"]
        
        except Exception as e:
            print(f"{PDAO_ERROR}Error al agregar el usuario: {e}")
            return False
        
    def update_usuario(self, usuario) -> bool:
        try:
            user_dict : dict = usuario.usuario_to_dict()
            user_dict["_id"] = user_dict.pop("id", None)
            result : pymongo.results.UpdateResult = self.collection.update_one({"_id": user_dict["_id"]}, {"$set": user_dict})
            return result.matched_count == 1
        
        except Exception as e:
            print(f"{PDAO_ERROR}Error al actualizar el usuario: {e}")
            return False
    
    def delete_usuario(self, id) -> bool:
        try:
            result : pymongo.results.DeleteResult = self.collection.delete_one({"_id": id})
            return result.deleted_count == 1
        
        except Exception as e:
            print(f"{PDAO_ERROR}Error al eliminar el usuario: {e}")
            return False