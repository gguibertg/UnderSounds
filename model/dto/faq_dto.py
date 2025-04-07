"""
Módulo DTO para representar preguntas frecuentes (FAQs).
Define clases para transportar y estructurar los datos de una o varias FAQs.
"""

import json


class FaqsDTO:
    """
    Contenedor de objetos FaqDTO.

    Esta clase almacena múltiples preguntas frecuentes y permite
    transformarlas a un formato JSON.
    """

    def __init__(self):
        """Inicializa la lista de FAQs vacía."""
        self.faq_list = []

    def insert_faq(self, faq):
        """
        Añade una FAQ a la lista.

        :param faq: Objeto de tipo FaqDTO
        """
        self.faq_list.append(faq)

    def faqs_to_json(self):
        """
        Devuelve las FAQs en formato JSON.

        :return: Cadena JSON con las FAQs
        """
        return json.dumps([faq.faq_to_dict() for faq in self.faq_list])


class FaqDTO:
    """
    Representa una pregunta frecuente individual.
    Contiene campos para el identificador, la pregunta y la respuesta.
    """

    def __init__(self):
        """Inicializa los atributos como None."""
        self.id = None
        self.question = None
        self.answer = None

    def is_empty(self):
        """
        Comprueba si todos los campos están vacíos.

        :return: True si todos los atributos son None, False en caso contrario
        """
        return self.id is None and self.question is None and self.answer is None

    def get_id(self):
        """Devuelve el ID de la FAQ."""
        return self.id

    def set_id(self, id_):
        """Establece el ID de la FAQ."""
        self.id = id_

    def get_question(self):
        """Devuelve la pregunta de la FAQ."""
        return self.question

    def set_question(self, question):
        """Establece la pregunta de la FAQ."""
        self.question = question

    def get_answer(self):
        """Devuelve la respuesta de la FAQ."""
        return self.answer

    def set_answer(self, answer):
        """Establece la respuesta de la FAQ."""
        self.answer = answer

    def faq_to_dict(self):
        """
        Convierte la FAQ a un diccionario, útil para la base de datos.

        :return: Diccionario con 'question' y 'answer'
        """
        return {
            "question": self.question,
            "answer": self.answer
        }
