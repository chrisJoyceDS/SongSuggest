import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os

CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
# REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")

class UserSession:
    
    def __init__(self):
        self.authed = False
        self.access_token = None

    def authenticate(self):

        client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        self.access_token = sp
        self.authed = True

