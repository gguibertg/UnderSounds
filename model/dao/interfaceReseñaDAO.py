from abc import ABC, abstractmethod
from ..dto.reseñasDTO import ReseñaDTO
from ..dto.songDTO import SongDTO

class InterfaceReseñaDAO(ABC):

    @abstractmethod
    def get_all_reseñas_song(self, song: SongDTO):
        pass

    @abstractmethod
    def get_reseña(self, id):
        pass

    @abstractmethod
    def get_reseña_song(self, id, song: SongDTO):
        pass

    @abstractmethod
    def add_reseña(self, reseña: ReseñaDTO):
        pass
    
    @abstractmethod
    def update_reseña(self, reseña: ReseñaDTO):
        pass

    @abstractmethod
    def delete_reseña(self, id):
        pass