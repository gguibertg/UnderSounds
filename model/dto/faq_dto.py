import json

class FaqsDTO:
    """
    Clase que representa una colección de objetos FaqDTO.
    
    Atributos:
        faqsList (list): Lista que almacena objetos FaqDTO serializados como diccionarios.
    """

    def __init__(self):
        """
        Inicializa una lista vacía para almacenar objetos FAQ.
        """
        self.faqsList = []

    def insert_faq(self, faq):
        """
        Inserta un objeto FAQ (como diccionario) en la lista de FAQs.

        Args:
            faq (dict): Diccionario que representa un objeto FaqDTO.
        """
        self.faqsList.append(faq)

    def faqList_to_json(self):
        """
        Convierte la lista de FAQs a formato JSON.

        Returns:
            str: Representación en cadena JSON de la lista de FAQs.
        """
        return json.dumps(self.faqsList)


class FaqDTO:
    """
    Clase que representa un objeto FAQ individual con ID, pregunta y respuesta.

    Atributos:
        id (int): Identificador único del FAQ.
        question (str): Pregunta del FAQ.
        answer (str): Respuesta asociada a la pregunta.
    """

    def __init__(self):
        """
        Inicializa un FAQ con valores None por defecto.
        """
        self.id = None
        self.question = None
        self.answer = None

    def is_empty(self):
        """
        Verifica si el objeto FAQ está vacío (sin datos).

        Returns:
            bool: True si todos los campos están en None, False en caso contrario.
        """
        return self.id is None and self.question is None and self.answer is None

    def get_id(self):
        """
        Obtiene el ID del FAQ.

        Returns:
            int: El identificador del FAQ.
        """
        return self.id

    def set_id(self, id):
        """
        Establece el ID del FAQ.

        Args:
            id (int): El nuevo identificador.
        """
        self.id = id

    def get_question(self):
        """
        Obtiene la pregunta del FAQ.

        Returns:
            str: La pregunta.
        """
        return self.question

    def set_question(self, question):
        """
        Establece la pregunta del FAQ.

        Args:
            question (str): La nueva pregunta.
        """
        self.question = question

    def get_answer(self):
        """
        Obtiene la respuesta del FAQ.

        Returns:
            str: La respuesta.
        """
        return self.answer

    def set_answer(self, answer):
        """
        Establece la respuesta del FAQ.

        Args:
            answer (str): La nueva respuesta.
        """
        self.answer = answer

    def faqdto_to_dict(self):
        """
        Convierte el objeto FAQ a un diccionario.

        Returns:
            dict: Diccionario con las claves 'id', 'question' y 'answer'.
        """
        return {
            "id": self.id,
            "question": self.question,
            "answer": self.answer
        }
