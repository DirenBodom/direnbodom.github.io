class SongClass:
    def __init__(self, artist, song, album, url: str = None):
        self.artist = artist
        self.song = song
        self.album = album
        self.image_url = url
