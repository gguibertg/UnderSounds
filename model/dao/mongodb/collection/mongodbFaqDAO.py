from ...interfaceFaqDAO import InterfaceFaqDAO
from ....dto.faqDTO import FaqDTO, FaqsDTO

class MongodbFaqDAO(InterfaceFaqDAO):

    def __init__(self, collection):
        self.collection = collection

    def get_all_faqs(self):
        faqs = FaqsDTO()

        try:
            query = self.collection.find()

            # doc ya es un diccionario en MongoDB.
            for doc in query:
                faq_dto = FaqDTO()
                faq_dto.set_id(str(doc.get("_id")))
                faq_dto.set_question(doc.get("question"))
                faq_dto.set_answer(doc.get("answer"))
                faqs.insertFaq(faq_dto)

        except Exception as e:
            print(f"Error al recuperar los FAQs: {e}")
            
        return [faq.faqdto_to_dict() for faq in faqs.faqsList]
