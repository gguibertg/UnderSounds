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
        self.id = None
        self.album = None
        self.artist = None
        self.collaborators = None
        self.date = None
        self.duration = None 
        self.genres = None
        self.likes = None
        self.price = None
        self.review_list = None
        self.title = None
        self.views = None

    def is_Empty(self):
        return (self.id is None and self.album is None and self.artist is None and 
                self.collaborators is None and self.date is None and self.duration is None and
                self.genres is None and self.likes is None and self.price is None and
                self.review_list is None and self.title is None is None and  self.views)

    def get_id(self):
        return self.id

    def set_id(self, id):
        self.id = id
    
    def get_album(self):
        return self.album

    def set_album(self, album):
        self.album = album

    def get_artist(self):
        return self.artist

    def set_artist(self, artist):
        self.artist = artist

    def get_collaborators(self):
        return self.collaborators

    def set_collaborators(self, collaborators):
        self.collaborators = collaborators

    def get_date(self):
        return self.date

    def set_date(self, date):
        self.date = date

    def get_duration(self):
        return self.duration

    def set_duration(self, duration):
        self.duration = duration

    def get_genres(self):
        return self.genres

    def set_genres(self, genres):
        self.genres = genres

    def get_likes(self):
        return self.likes

    def set_likes(self, likes):
        self.likes = likes

    def get_price(self):
        return self.price

    def set_price(self, price):
        self.price = price

    def get_review_list(self):
        return self.review_list

    def set_review_list(self, review_list):
        self.review_list = review_list

    def get_title(self):
        return self.title

    def set_title(self, title):
        self.title = title

    def get_views(self):
        return self.views

    def set_views(self, views):
        self.views = views

    # Por último, definimos una función que se va a usar para convertir la canción a un diccionario.
    def songdto_to_dict(self):
        return {
            "id": self.id,
            "album": self.album,
            "artist": self.artist,
            "collaborators": self.collaborators,
            "date": self.date,
            "duration": self.duration,
            "genres": self.genres,
            "likes": self.likes,
            "price": self.price,
            "review_list": self.review_list,
            "title": self.title,
            "views": self.views
        }
    
