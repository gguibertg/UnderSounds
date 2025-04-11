import json

# La clase SongsDTO es la que se va a usar para almacenar las canciones que se van a devolver al cliente.
class SongsDTO():
    # Al crear la clase definimos una lista vacía que se va a usar para almacenar las canciones.
    def __init__(self):
        self.songlist = []

    # Definimos una función que se va a usar para añadir canciones a la lista de canciones.
    def insertSong(self, elem):
        self.songlist.append(elem)

    # Y otra para convertirla a JSON.
    def songlist_to_json(self):
        return json.dumps(self.songlist)

# La clase SongDTO es la que se va a usar para almacenar los datos de una canción.
class SongDTO():

    # Al crear la clase definimos los atributos que se van a usar para almacenar los datos de la canción.
    def __init__(self):
        self.album = None
        self.author = None
        self.id = None
        self.duration = None  # Corregido (antes length)
        self.musicgenre = None
        self.price = None
        self.rating = None
        self.release = None
        self.title = None

    # Definimos una función que se va a usar para comprobar si la canción está vacía.
    def is_Empty(self):
        return (self.album is None and self.author is None and self.id is None and
                self.duration is None and self.musicgenre is None and self.price is None and
                self.rating is None and self.release is None and self.title is None)

    # Otra para devolver el atributo album.
    def get_album(self):
        return self.album

    # Otra para establecer el atributo album...
    def set_album(self, album):
        self.album = album

    # ...y así con el resto de atributos.
    def get_author(self):
        return self.author

    def set_author(self, author):
        self.author = author

    def get_id(self):
        return self.id

    def set_id(self, id):
        self.id = id

    def get_duration(self):
        return self.duration

    def set_duration(self, duration):
        self.duration = duration

    def get_musicgenre(self):
        return self.musicgenre

    def set_musicgenre(self, musicgenre):
        self.musicgenre = musicgenre

    def get_price(self):
        return self.price

    def set_price(self, price):
        self.price = price

    def get_rating(self):
        return self.rating

    def set_rating(self, rating):
        self.rating = rating

    def get_release(self):
        return self.release

    def set_release(self, release):
        self.release = release

    def get_title(self):
        return self.title

    def set_title(self, title):
        self.title = title

    # Por último, definimos una función que se va a usar para convertir la canción a un diccionario.
    def songdto_to_dict(self):
        return {
            "album": self.album,
            "author": self.author,
            "id": self.id,
            "duration": self.duration,
            "musicgenre": self.musicgenre,
            "price": self.price,
            "rating": self.rating,
            "release": str(self.release),
            "title": self.title
        }
    
