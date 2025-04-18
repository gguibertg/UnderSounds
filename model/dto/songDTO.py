import json

class SongsDTO():
    def __init__(self):
        self.songlist = []

    def get_songlist(self):
        return self.songlist

    def insertSong(self, elem):
        self.songlist.append(elem)

    def songlist_to_json(self):
        return json.dumps(self.songlist)

class SongDTO():

    def __init__(self):
        self.id: str = None
        self.artist: str = None
        self.collaborators: list[str] = []
        self.date: str = None
        self.description: str = None
        self.duration: str = None 
        self.genres: list[str] = []
        self.likes: int = None
        self.portada: str = None
        self.price: float = None
        self.review_list: list[str] = []
        self.title: str = None
        self.views: int = None

    def is_Empty(self):
        return (self.id is None and self.artist is None and 
                self.collaborators is None and self.date is None and self.description is None and 
                self.duration is None and self.genres is None and self.likes is None and self.portada is None and 
                self.price is None and self.review_list is None and self.title is None is None and  self.views)

    def get_id(self) -> str:
        return self.id

    def set_id(self, id: str):
        self.id = id

    def get_artist(self) -> str:
        return self.artist

    def set_artist(self, artist: str):
        self.artist = artist

    def get_collaborators(self) -> list[str]:
        return self.collaborators

    def set_collaborators(self, collaborators: list[str]):
        self.collaborators = collaborators

    def get_date(self) -> str:
        return self.date

    def set_date(self, date: str):
        self.date = date

    def get_description(self) -> str:
        return self.description

    def set_description(self, description: str):
        self.description = description

    def get_duration(self) -> str:
        return self.duration

    def set_duration(self, duration: str):
        self.duration = duration

    def get_genres(self) -> list[str]:
        return self.genres

    def add_genero(self, genero_id: str):
        self.genres.append(genero_id)

    def remove_genero(self, genero_id: str):
        if genero_id in self.genres:
            self.genres.remove(genero_id)

    def set_genres(self, genres: list[str]):
        self.genres = genres

    def get_likes(self) -> int:
        return self.likes

    def set_likes(self, likes: int):
        self.likes = likes

    def get_portada(self) -> str:
        return self.portada

    def set_portada(self, portada: str):
        self.portada = portada

    def get_price(self) -> float:
        return self.price

    def set_price(self, price: float):
        self.price = price

    def get_review_list(self) -> list[str]:
        return self.review_list

    def set_review_list(self, review_list: list[str]):
        self.review_list = review_list

    def get_title(self) -> str:
        return self.title

    def set_title(self, title: str):
        self.title = title

    def get_views(self) -> int:
        return self.views

    def set_views(self, views: int):
        self.views = views

    # Por último, definimos una función que se va a usar para convertir la canción a un diccionario.
    def songdto_to_dict(self) -> dict:
        return {
            "id": self.id,
            "artist": self.artist,
            "collaborators": self.collaborators,
            "date": self.date,
            "description": self.description,
            "duration": self.duration,
            "genres": self.genres,
            "likes": self.likes,
            "portada": self.portada,
            "price": self.price,
            "review_list": self.review_list,
            "title": self.title,
            "views": self.views
        }
