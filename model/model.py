from .dao.mongodb.mongodbDAOFactory import mongodbDAOFactory
from .dto.usuarioDTO import UsuarioDTO, UsuariosDTO

# La clase Model tiene los métodos que hacen puente entre controller y la base de datos.
class Model ():

    def __init__(self):
        self.factory = mongodbDAOFactory()
        self.daoUsuario = self.factory.getUsuariosDAO()
        pass
    
    def get_usuario(self, id):
        return self.daoUsuario.get_usuario(id)
    
    def add_usuario(self, usuario : UsuarioDTO):
        return self.daoUsuario.add_usuario(usuario)

    def update_usuario(self, usuario : UsuarioDTO):
        return self.daoUsuario.update_usuario(usuario)

    def delete_usuario(self, id):
        return self.daoUsuario.delete_usuario(id)

    def get_usuarios(self):
        return self.daoUsuario.get_all_usuarios()

