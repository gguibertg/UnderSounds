from datetime import datetime
from .dao.mongodb.mongodbDAOFactory import MongodbDAOFactory
from .dto.albumDTO import AlbumDTO
from .dto.generoDTO import GeneroDTO
from .dto.songDTO import SongDTO, SongsDTO
from .dto.usuarioDTO import UsuarioDTO, UsuariosDTO
from .dto.contactoDTO import ContactoDTO
from .dto.reseñasDTO import ReseñaDTO
from .dto.carritoDTO import ArticuloCestaDTO
from .dto.sesionDTO import SesionDTO



# La clase Model tiene los métodos que hacen puente entre controller y la base de datos.
class Model ():

    def __init__(self):
        self.factory = MongodbDAOFactory()
        self.songsDAO = self.factory.getSongsDAO()
        self.daoUsuario = self.factory.getUsuariosDAO()
        self.faqsDAO = self.factory.getFaqsDAO()
        self.daoAlbum = self.factory.getAlbumDAO()
        self.daoGenero = self.factory.getGeneroDAO()
        self.songsDAO = self.factory.getSongsDAO()
        self.carrito = self.factory.getCarritoDAO()
        self.daoContacto = self.factory.getContactoDAO()
        self.daoReseña = self.factory.getReseñaDAO()
        self.daoSesion = self.factory.getSesionDAO()
        pass

    # Usuario
    def get_usuario(self, id : str):
        return self.daoUsuario.get_usuario(id)
    def get_artistas(self):
        return self.daoUsuario.get_artistas()
    def get_usuarios_by_fecha(self, fecha):
        return self.daoUsuario.get_all_by_fecha(fecha)
    def get_usuarios_by_nombre(self, nombre):
        return self.daoUsuario.get_all_by_nombre(nombre)
    def add_usuario(self, usuario : UsuarioDTO):
        return self.daoUsuario.add_usuario(usuario)
    def get_usuarios_by_song(self, song_id):
        return self.daoUsuario.get_all_usuarios_by_song(song_id)
    def get_usuarios_by_song_in_list(self, song_id):
        return self.daoUsuario.get_all_usuarios_by_song_in_list(song_id)
    def update_usuario(self, usuario : UsuarioDTO):
        return self.daoUsuario.update_usuario(usuario)
    def delete_usuario(self, id : str):
        return self.daoUsuario.delete_usuario(id)
    # === Listas de reproducción ===

    def add_lista_usuario(self, user_id: str, nombre_lista: str):
        usuario_dict = self.daoUsuario.get_usuario(user_id)
        usuario_dto = UsuarioDTO()
        usuario_dto.load_from_dict(usuario_dict)
        usuario_dto.add_lista_reproduccion(nombre_lista)
        self.daoUsuario.update_usuario(usuario_dto)

    def remove_lista_usuario(self, user_id: str, nombre_lista: str):
        usuario_dict = self.daoUsuario.get_usuario(user_id)
        usuario_dto = UsuarioDTO()
        usuario_dto.load_from_dict(usuario_dict)
        usuario_dto.remove_lista_reproduccion(nombre_lista)
        self.daoUsuario.update_usuario(usuario_dto)

    def add_cancion_a_lista_usuario(self, user_id: str, nombre_lista: str, id_cancion: str):
        usuario_dict = self.daoUsuario.get_usuario(user_id)
        usuario_dto = UsuarioDTO()
        usuario_dto.load_from_dict(usuario_dict)
        usuario_dto.add_song_to_lista_reproduccion(nombre_lista, id_cancion)
        self.daoUsuario.update_usuario(usuario_dto)

    def remove_cancion_de_lista_usuario(self, user_id: str, nombre_lista: str, id_cancion: str):
        usuario_dict = self.daoUsuario.get_usuario(user_id)
        usuario_dto = UsuarioDTO()
        usuario_dto.load_from_dict(usuario_dict)
        usuario_dto.remove_song_from_lista_reproduccion(nombre_lista, id_cancion)
        self.daoUsuario.update_usuario(usuario_dto)

    def get_usuarios_by_song(self, song_id):
        return self.daoUsuario.get_all_usuarios_by_song(song_id)
    
    def get_usuarios_by_song_in_list(self, song_id):
        return self.daoUsuario.get_all_usuarios_by_song_in_list(song_id)

    # Faqs
    def get_faqs(self):
        return self.faqsDAO.get_all_faqs()

    # Contacto
    def add_contacto(self, contacto : ContactoDTO):
        return self.daoContacto.add_contacto(contacto)
    
    # Carrito
    def get_carrito(self, usuario : str):
        return self.carrito.get_all_articulos(usuario)
    
    def upsert_articulo(self, usuario, articulo: ArticuloCestaDTO):
        return self.carrito.upsert_articulo_en_carrito(usuario, articulo)
    
    def articulo_existe(self, carrito: dict, articulo_id: str):
        return self.carrito.articulo_existe_en_carrito(carrito, articulo_id)

    def agregar_articulo(self, usuario, articulo_dict):
        return self.carrito.agregar_articulo_a_carrito(usuario, articulo_dict)
    
    def crear_carrito(self, usuario, articulo_dict):
        return self.carrito.crear_carrito(usuario, articulo_dict)
    
    def vaciar_carrito(self, usuario: str):
        return self.carrito.vaciar_carrito(usuario)
    
    def deleteArticulo(self, usuario, id_articulo):
        return self.carrito.deleteArticuloDelCarrito(usuario, id_articulo)

    # Album
    def get_albums(self):
        return self.daoAlbum.get_all_albums()
    def get_albums_by_genre(self, genre):
        return self.daoAlbum.get_all_by_genre(genre)
    def get_albums_by_fecha(self, fecha):
        return self.daoAlbum.get_all_by_fecha(fecha)
    def get_albums_by_titulo(self, titulo):
        return self.daoAlbum.get_all_by_nombre(titulo)
    def get_album(self, id : str):
        return self.daoAlbum.get_album(id)
    def add_album(self, album : AlbumDTO):
        return self.daoAlbum.add_album(album)
    def update_album(self, album : AlbumDTO):
        return self.daoAlbum.update_album(album)
    def delete_album(self, id : str):
        return self.daoAlbum.delete_album(id)
    
    # Genero
    def get_genero(self, id : str):
        return self.daoGenero.get_genero(id)

    def get_generos(self):
        return self.daoGenero.get_generos()
    
    # Songs
    def get_song(self, id: str):
        return self.songsDAO.get_song(id)
    
    def add_song(self, usuario : SongDTO):
        return self.songsDAO.add_song(usuario)

    def update_song(self, usuario : SongDTO):
        return self.songsDAO.update_song(usuario)

    def delete_song(self, id : str):
        return self.songsDAO.delete_song(id)

    def get_songs(self):
        return self.songsDAO.get_all_songs()

    def get_songs_by_genre(self, genre: str):
        return self.songsDAO.get_all_by_genre(genre)
    
    def get_songs_by_fecha(self, fecha : datetime):
        return self.songsDAO.get_all_by_fecha(fecha)

    def get_songs_by_titulo(self, titulo : str):
        return self.songsDAO.get_all_by_nombre(titulo)
        
    #Reseña
    def get_all_reseñas_song(self, song: SongDTO):
        return self.daoReseña.get_all_reseñas_song(song)

    def get_reseña(self, id):
        return self.daoReseña.get_reseña(id)

    def get_reseña_song(self, id, song: SongDTO):
        return self.daoReseña.get_reseña_song(id, song)

    def add_reseña(self, reseña: ReseñaDTO):
        return self.daoReseña.add_reseña(reseña)
    
    def update_reseña(self, reseña: ReseñaDTO):
        return self.daoReseña.update_reseña(reseña)

    def delete_reseña(self, id):
        return self.daoReseña.delete_reseña(id)
    
    # Sesiones
    def get_all_sesiones(self):
        return self.daoSesion.get_all_sesiones()

    def get_sesion(self, id : str):
        return self.daoSesion.get_sesion(id)
    
    def add_sesion(self, sesion : SesionDTO):
        return self.daoSesion.add_sesion(sesion)
    
    def update_sesion(self, sesion : SesionDTO):
        return self.daoSesion.update_sesion(sesion)
    
    def delete_sesion(self, id : str):
        return self.daoSesion.delete_sesion(id)
    
    