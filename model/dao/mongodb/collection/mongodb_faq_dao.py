from ....dao.interface_faq_dao import InterfaceFaqDAO
from ....dto.faq_dto import FaqDTO, FaqsDTO
from ..mongodb_connector import db


class MongodbFaqDAO(InterfaceFaqDAO):
    """
    Implementación del DAO de FAQs utilizando MongoDB.

    Esta clase implementa las operaciones CRUD definidas en la interfaz InterfaceFaqDAO
    y accede directamente a la colección 'faqs' de la base de datos MongoDB.
    """

    def __init__(self):
        """
        Constructor que establece la conexión con la colección 'faqs' en MongoDB.
        Lanza una excepción si no se ha podido establecer la conexión.
        """
        if db is None:
            raise ConnectionError("❌ No se pudo conectar a MongoDB.")
        self.collection = db["Preguntas"]

    def get_faqs(self):
        """
        Recupera todas las FAQs almacenadas en la colección.

        Returns:
            str: FAQs en formato JSON (serializadas desde FaqsDTO).
        """
        faqs = FaqsDTO()
        try:
            cursor = self.collection.find()
            for doc in cursor:
                faq_dto = FaqDTO()
                faq_dto.set_id(doc.get("id", str(doc.get("_id"))))
                faq_dto.set_question(doc.get("question", ""))
                faq_dto.set_answer(doc.get("answer", ""))
                faqs.insert_faq(faq_dto.faqdto_to_dict())
        except Exception as e:
            print(f"Error al recuperar FAQs: {e}")
        return faqs.faqList_to_json()

    def get_faq_by_id(self, faq_id):
        """
        Busca una FAQ por su ID.

        Args:
            faq_id (int): ID de la FAQ a buscar.

        Returns:
            dict or None: Diccionario con los datos de la FAQ si se encuentra, None en caso contrario.
        """
        try:
            doc = self.collection.find_one({"id": faq_id})
            if doc:
                faq_dto = FaqDTO()
                faq_dto.set_id(doc.get("id"))
                faq_dto.set_question(doc.get("question", ""))
                faq_dto.set_answer(doc.get("answer", ""))
                return faq_dto.faqdto_to_dict()
        except Exception as e:
            print(f"Error al obtener FAQ por ID: {e}")
        return None

    def insert_faq(self, faq):
        """
        Inserta una nueva FAQ en la colección.

        Args:
            faq (FaqDTO): Objeto con los datos de la FAQ.
        """
        try:
            faq_dict = faq.faqdto_to_dict()
            self.collection.insert_one(faq_dict)
        except Exception as e:
            print(f"Error al insertar FAQ: {e}")

    def update_faq(self, faq_id, updated_faq):
        """
        Actualiza una FAQ existente por su ID.

        Args:
            faq_id (int): ID de la FAQ a actualizar.
            updated_faq (FaqDTO): Objeto con los nuevos datos.

        Returns:
            bool: True si la actualización fue exitosa, False en caso contrario.
        """
        try:
            result = self.collection.update_one(
                {"id": faq_id},
                {"$set": updated_faq.faqdto_to_dict()}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error al actualizar FAQ: {e}")
            return False

    def delete_faq(self, faq_id):
        """
        Elimina una FAQ por su ID.

        Args:
            faq_id (int): ID de la FAQ a eliminar.

        Returns:
            bool: True si se eliminó correctamente, False si no se encontró.
        """
        try:
            result = self.collection.delete_one({"id": faq_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error al eliminar FAQ: {e}")
            return False
