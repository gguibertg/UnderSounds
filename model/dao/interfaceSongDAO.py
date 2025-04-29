from abc import ABC, abstractmethod
from ..dto.songDTO import SongDTO

class InterfaceSongDAO(ABC):

    @abstractmethod
    def get_all_songs(self):
        pass

    @abstractmethod
    def get_song(self, id):
        pass

    @abstractmethod
    def add_song(self, song: SongDTO):
        pass
    
    @abstractmethod
    def update_song(self, song: SongDTO):
        pass

    @abstractmethod
    def delete_song(self, id):
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