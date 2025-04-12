from .dao.mongodb.mongodbDAOFactory import mongodbDAOFactory
from .dto.usuarioDTO import UsuarioDTO, UsuariosDTO

# La clase Model es la encargada de gestionar los datos y la lógica de negocio de la aplicación.
# Esta clase nos permite interactuar con la base de datos y obtener los datos que necesitamos para la aplicación,
# sin la necesidad de que otras clases tengan que preocuparse por la implementación de la base de datos.
class Model ():

    # Al crear la clase definimos factores y DAOs que vamos a usar para interactuar con la base de datos.
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

