import json

class FaqsDTO:
    def __init__(self):
        self.faqsList = []

    def insertFaq(self, faq):
        self.faqsList.append(faq)

    def faqList_to_json(self):
        return json.dumps(self.faqsList)

class FaqDTO:
    def __init__(self):
        self.id = None
        self.question = None
        self.answer = None

    def is_empty(self):
        return (self.id is None and self.question is None and self.answer is None)

    def get_id(self):
        return self.id

    def set_id(self, id):
        self.id = id

    def get_question(self):
        return self.question

    def set_question(self, question):
        self.question = question

    def get_answer(self):
        return self.answer

    def set_answer(self, answer):
        self.answer = answer

    def faqdto_to_dict(self):
        return {
            "id": self.id,
            "question": self.question,
            "answer": self.answer
        }
