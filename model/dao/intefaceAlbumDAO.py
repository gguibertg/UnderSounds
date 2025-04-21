from abc import ABC, abstractmethod

class InterfaceAlbumDAO(ABC):

    @abstractmethod	
    def get_album(self, id):
        pass

    @abstractmethod
    def add_album(self, album):
        pass

    @abstractmethod
    def update_album(self, album):
        pass

    @abstractmethod
    def delete_album(self, id):
        pass