from .dao.mongodb.mongodbDAOFactory import mongodbDAOFactory
from .dto.usuarioDTO import UsuarioDTO

# La clase Model tiene los métodos que hacen puente entre controller y la base de datos.
class Model ():

    def __init__(self):
        self.factory = mongodbDAOFactory()
        self.daoUsuario = self.factory.getUsuariosDAO()
        self.faqsDAO = self.factory.getFaqsDAO()
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

    def get_faqs(self):
        return self.faqsDAO.get_all_faqs()

    # TODO: Esta función se va a usar para guardar el mensaje de contacto en la base de datos.
    # La función recibe el nombre, el email, el teléfono y el mensaje del contacto.
    # La función devuelve True si se ha guardado correctamente y False si ha habido un error.
    def save_contact_msg(self, name: str, email: str, telf: str, msg: str):
        return True