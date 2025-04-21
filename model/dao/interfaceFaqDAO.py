from abc import ABC, abstractmethod

class InterfaceFaqDAO(ABC):

    @abstractmethod
    def get_all_faqs(self):
        pass