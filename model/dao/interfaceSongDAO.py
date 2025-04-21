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

