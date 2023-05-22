# Next, Tracks, and Playlist Code Referenced from:
# https://stackoverflow.com/questions/39086287/spotipy-how-to-read-more-than-100-tracks-from-a-playlist
import spotipy
import spotipy.oauth2 as oauth2
import os
import pandas as pd
from spotipy.exceptions import SpotifyException

# load Spotify OAuth credentials from .env file
from dotenv import load_dotenv
load_dotenv()
CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")

######################################################################################################
# Authentication Method
######################################################################################################

# Define function to authenticate user with Spotify
def authenticate(scope):
    """
    Instantiates a connection object through Spotipy for a Spotify Web API session. Uses env variables
    for client, client secret, and client redirect URI to handle request. Checks to see if there is a cached token for use. If there is, sets the access token to the current cached token. If not, it retrieves an authorization url to redirect the user to, and creates a prompt for the user to paste the code in from the site they visited. After code is entered, retrieves an access token via the auth_code provided, and saves it as an access token. Finally a Spotify session object is created with the access token which last 1hr before needing to be refreshed.
    :param scope: a scope string which provides different access to different calls and data from Spotify.
    :return sp: a spotipy.Spotify object with an access token for the user
    """
    # set up OAuth2 flow
    auth = oauth2.SpotifyOAuth(client_id=CLIENT_ID,
                               client_secret=CLIENT_SECRET,
                               redirect_uri=REDIRECT_URI,
                               scope=scope)
    # check if there is a cached access token
    cached_token = auth.get_cached_token()
    # if cached token is populated
    if cached_token:
        # used cache token
        access_token = cached_token['access_token']
    else:
        # get authorization URL and prompt user to authorize the app
        auth_url = auth.get_authorize_url()
        print(f"Please authorize the app by visiting this URL: {auth_url}")
        auth_code = input("Enter the authorization code: ")

        # exchange authorization code for access token and refresh token
        tokens = auth.get_access_token(auth_code)
        access_token = tokens['access_token']
    # refresh_token = tokens['refresh_token']

    # create a Spotify object using the access token
    sp = spotipy.Spotify(auth=access_token)

    return sp


######################################################################################################
# Playlist Retrieval Methods
######################################################################################################

def get_user_playlists(sp):
    """
    Retrieves the current user's id and passes it to pull their owned or followed playlists
    :param sp: a spotipy.Spotify object with an access token for the user
    :return playlist_ids: a list of playlist ids
    :return playlist_names: a list of associated playlist names
    """
    # get user's id
    user_id = sp.current_user()["id"]
    # get the user's playlists
    playlists = sp.user_playlists(user=user_id)
    # set empty list of playlist ids
    playlist_ids = []
    # set empty list of playlist names
    playlist_names = []
    # loop through playlists
    for playlist in playlists['items']:
        # append id
        playlist_ids.append(playlist['id'])
        
    return playlist_ids

    
######################################################################################################
# Track Retrieval Methods
######################################################################################################

# Saved Tracks
def get_saved_tracks_df(sp):
    """
    Retrieves the user's saved or liked tracks from their profile and adds them to a DataFrame.
    :param sp: a spotipy.Spotify object with an access token for the user
    :return df: a pandas DataFrame containing track ID, track name, track artists, track album and other metadata.
    """
    # sets results to the first call of 20 where offset = 0
    results = sp.current_user_saved_tracks(limit=20, offset=0)
    # saves tracks from call by calling items key
    tracks = results['items']
    # response returns url to the next page of items, while populated
    while results['next']:
        # call next reults 
        results = sp.next(results)
        # extend current tracks list by new results
        tracks.extend(results['items'])
    # set new list for flattened observations
    flattened_tracks = []
    # iterate through the tracks
    for track in tracks:
        # unlock track info by calling track key
        track_info = track['track']
        # set columns and info for observation per track
        flattened_track = {
            "id": track_info["id"],
            "track_name": track_info["name"],
            "artist": track_info["artists"][0]["name"],
            "artist_uri": track_info["artists"][0]["uri"],
            "album_uri": track_info["album"]["uri"],
            "album": track_info["album"]["name"],
            "release_date": track_info["album"]["release_date"],
            "popularity": track_info["popularity"],
            "explicit": track_info["explicit"]
        }
        # append newly flattened observation into flattened tracks list
        flattened_tracks.append(flattened_track)
    # turn flattened tracks into pandas df and return
    df = pd.DataFrame(flattened_tracks)
    df['user_liked'] = 1
    return df

def get_all_playlist_tracks(sp, playlist_id):
    """
    Retrieves the tracks contained in a playlist object by passing the playlist id
    :param sp: a spotipy.Spotify object with an access token for the user
    :param playlist_id: id associated to a specific Spotify playlist
    :return tracks: a list of track objects from the current playlist
    """
    # results = specific playlist
    results = sp.playlist_items(playlist_id)
    # tracks equals items key value pair
    tracks = results['items']
    # the playlist_tracks call has a limit of 100,
    # when there are more tracks, the response contains a next url
    while results['next']:
        # the next function takes a previous paged result and generates the next
        results = sp.next(results)
        # extend tracks by next call
        tracks.extend(results['items'])
    # return tracks
    return tracks


# Flatten Tracks:
def flatten_tracks(tracks):
    
    flattened_tracks = []
    
    for track in tracks:

        try:
           
            flattened_track = {
                    "id": track["track"]["id"],
                    "track_name": track["track"]["name"],
                    "artist": track["track"]["artists"][0]["name"],
                    "artist_uri": track["track"]["artists"][0]["uri"],
                    "album_uri": track["track"]["album"]["uri"],
                    "album": track["track"]["album"]["name"],
                    "release_date": track["track"]["album"]["release_date"],
                    "popularity": track["track"]["popularity"],
                    "explicit": track["track"]["explicit"],
                    "user_liked": 1
                }
            
            flattened_tracks.append(flattened_track)
        except:
            continue
            
    return flattened_tracks


# User Playlist Tracks
def get_user_playlist_tracks(sp):
    """
    Retrieves the user's playlists and tracks for each playlist and adds them to a DataFrame.
    :param sp: a spotipy.Spotify object with an access token for the user
    :param df: a dataframe made up of a user's liked tracks and their audio features
    :return: a pandas DataFrame containing playlist name, track ID, track name, and track artists
    """
    # get lists of playlist ids 
    playlist_ids = get_user_playlists(sp)
    
    # set new list for flattened tracks
    tracks = []
    # loop through zippled playlist ids and names
    for playlist_id in playlist_ids:
        # get tracks from playlist
        tracks.extend(get_all_playlist_tracks(sp, playlist_id))
        
    
    # turn flattened tracks into pandas df and return
    playlist_tracks_df = pd.DataFrame(flatten_tracks(tracks))

        
    return playlist_tracks_df

# Featured Playlists:
def get_featured_playlist_tracks_df(sp, df):
    """
    Retrieves featured Spotify playlists from default available markets
    :param sp: a spotipy.Spotify object with an access token for the user
    :param df: a pandas Dataframe containing a given users tracks, track metadata, track audio features
    :return: a pandas DataFrame containing a users tracks, track metadata, track audio features, and tracks from Spotify's featured playlists
    """
    pass
    


# Audio Track Features Retrieval
def get_track_audio_features(sp, df):
    """
    Retrieves a set of track audio features from a provided dataframe and merges the results
    :param sp: a spotipy.Spotify object with an access token for the user
    :param df: a pandas Dataframe containing a given users tracks and associated track metadata features.
    :return tracks_w_features: a pandas DataFrame containing a users tracks, track metadata and track audio features.
    """
    # Use List Comprehension to get List of all track ids
    track_ids = [track for track in df['id']]
    # set list for audio features
    audio_features = []
    # iterate through list of track ids 100 at a time to account for api call limit
    for i in range(0, len(track_ids), 100):
        # get batch of audio features for each chunk of 100
        audio_features_batch = sp.audio_features(tracks=track_ids[i:i+100])
        # add batch to audio features
        audio_features += audio_features_batch
    # turn audio features into a df
    audio_features_df = pd.DataFrame(audio_features)
    # drop columns we dont need
    audio_features_df = audio_features_df.drop(columns=['type', 'uri', 'track_href', 'analysis_url'])
    # merge original df and audio features df
    tracks_w_features = merger(df, audio_features_df)
    # return df
    return tracks_w_features

######################################################################################################
# Handler Methods
######################################################################################################
# Having created multiple methods for different calls, I wanted to create a handler function that would
# process the function calls, passing the token and parameters for me so I can focus on the intense
# aspects of this process such as modeling. This provides me with a scalable architecture should
# additional needs arise.

FUNCTION_MAP = {
    
    "get_saved_tracks": {'function': get_saved_tracks_df,
                         'scope': 'user-library-read',
                         'params': 'no'},
    "get_track_audio_features": {'function': get_track_audio_features,
                                 'scope': 'user-library-read',
                                 'params': 'yes'},
    "get_user_playlist_tracks": {'function': get_user_playlist_tracks,
                               'scope': 'user-library-read playlist-read-private',
                                 'params': 'no'},
}

def handler(identifier, df=None):
    # check if the identifier is valid
    if identifier not in FUNCTION_MAP:
        raise ValueError(f"Invalid identifier: {identifier}")
    # set function to saved function associated to identifier
    function = FUNCTION_MAP[identifier]['function']
    # set token using scope from Function Map
    token = authenticate(FUNCTION_MAP[identifier]['scope'])
    # if function doesnt need additional params (so far df):
    if FUNCTION_MAP[identifier]['params'] == 'no':
        # call the appropriate function with the Spotify object
        return FUNCTION_MAP[identifier]['function'](token)
    else:
        # call the appropriate function with the Spotify object
        return FUNCTION_MAP[identifier]['function'](token, df)
    
def merger(df, df1):
    """
    Merges two provided dataframes on an inner join on id
    :param df: a pandas Dataframe containing a given users tracks and associated track metadata features.
    :param df1: a pandas Dataframe containing a given users tracks and associated track audio features.
    :return: a pandas DataFrame containing a users tracks, track metadata and track audio features.
    """
    # if records of id already exist in the first df
    # merge inner on id to keep items on the left
    return pd.merge(df, df1, on='id', how='inner', suffixes=('',''))

