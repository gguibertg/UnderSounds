from .dao.mongodb.mongodbDAOFactory import mongodbDAOFactory
from .dto.usuarioDTO import UsuarioDTO, UsuariosDTO
from .dto.albumDTO import AlbumDTO
from .dto.generoDTO import GeneroDTO
from .dto.songDTO import SongDTO


# La clase Model tiene los métodos que hacen puente entre controller y la base de datos.
class Model ():

    def __init__(self):
        self.factory = mongodbDAOFactory()
        self.daoUsuario = self.factory.getUsuariosDAO()
        self.faqsDAO = self.factory.getFaqsDAO()
        self.daoAlbum = self.factory.getAlbumDAO()
        self.daoGenero = self.factory.getGeneroDAO()
        self.songsDAO = self.factory.getSongsDAO()
        self.carrito = self.factory.getCarritoDAO()
        pass
    
    # Usuario
    def get_usuario(self, id):
        return self.daoUsuario.get_usuario(id)
    def add_usuario(self, usuario : UsuarioDTO):
        return self.daoUsuario.add_usuario(usuario)
    def update_usuario(self, usuario : UsuarioDTO):
        return self.daoUsuario.update_usuario(usuario)
    def delete_usuario(self, id):
        return self.daoUsuario.delete_usuario(id)
    # Sin uso
    def get_usuarios(self):
        return self.daoUsuario.get_all_usuarios()

    # Faqs
    def get_faqs(self):
        return self.faqsDAO.get_all_faqs()

    # TODO: Esta función se va a usar para guardar el mensaje de contacto en la base de datos.
    # La función recibe el nombre, el email, el teléfono y el mensaje del contacto.
    # La función devuelve True si se ha guardado correctamente y False si ha habido un error.
    def save_contact_msg(self, name: str, email: str, telf: str, msg: str):
        return True
    
    def get_carrito(self, usuario):
        return self.carrito.get_all_articulos(usuario)
    
    # Album
    def get_album(self, id):
        return self.daoAlbum.get_album(id)
    def add_album(self, album : AlbumDTO):
        return self.daoAlbum.add_album(album)
    def update_album(self, album : AlbumDTO):
        return self.daoAlbum.update_album(album)
    def delete_album(self, id):
        return self.daoAlbum.delete_album(id)
    
    # Genero
    def get_genero(self, id):
        return self.daoGenero.get_genero(id)
    
    # Songs
    def get_song(self, id: str):
        return self.songsDAO.get_song(id)
    
    def add_song(self, usuario : SongDTO):
        return self.songsDAO.add_song(usuario)

    def update_song(self, usuario : SongDTO):
        return self.songsDAO.update_song(usuario)

    def delete_song(self, id):
        return self.songsDAO.delete_song(id)

    def get_songs(self):
        return self.songsDAO.get_all_songs()