from abc import ABC, abstractmethod

class InterfaceAlbumDAO(ABC):

    @abstractmethod
    def get_all_albums(self):
        pass

    @abstractmethod
    def get_all_by_genre(self, genre):
        pass

    @abstractmethod
    def get_all_by_fecha(self, fecha):
        pass

    @abstractmethod
    def get_all_by_nombre(self, titulo):
        pass
    
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