from abc import ABC, abstractmethod

class InterfaceSongDAO(ABC):

    @abstractmethod
    def get_all_songs(self):
        pass