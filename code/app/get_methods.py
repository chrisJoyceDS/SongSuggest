# Next, Tracks, and Playlist Code Referenced from:
# https://stackoverflow.com/questions/39086287/spotipy-how-to-read-more-than-100-tracks-from-a-playlist
from user_session import UserSession
import spotipy
import spotipy.oauth2 as oauth2
import pandas as pd
from spotipy.exceptions import SpotifyException


######################################################################################################
# Search for Track
######################################################################################################
def search_genre_tracks(sp: object, genres):
    tracks_to_flat = []
    
    for i, genre in genres.iterrows():
        q = f"genre:{genre['genre']}"
        results = sp.search(q=q, type='track')
        tracks_to_flat.extend(results['tracks']['items'])
        
    tracks_for_model = prepare_tracks_for_model(sp, tracks_to_flat)  

    return tracks_for_model



def search_artist_tracks(sp: object, artists):
    tracks_to_flat = []
    
    for i, artist in artists.iterrows():
        q = f"artist:{artist['artist_name']}"
        results = sp.search(q=q, type='artist')
        top_tracks = sp.artist_top_tracks(artist_id=results['artists']['items'][0]['uri'],country='US')
        tracks_to_flat.extend(top_tracks['tracks'])
        
    tracks_for_model = prepare_tracks_for_model(sp, tracks_to_flat)   

    return tracks_for_model


def search_tracks(sp: object, tracks):
    tracks_to_flat = []
    for i, track in tracks.iterrows():
        q = f"track:{track['name']} artist:{track['artist']} year:{track['year']}"
        results = sp.search(q=q, type='track')
        track_object = sp.track(results['tracks']['items'][0]['id'])
        tracks_to_flat.append(track_object)
        
    tracks_for_model = prepare_tracks_for_model(sp, tracks_to_flat)

    return tracks_for_model

def flatten_tracks(tracks: list):

    # set new list for flattened observations
    flattened_tracks = []
    # iterate through the tracks
    for track in tracks:
        
        # set columns and info for observation per track
        try:
            flattened_track = {
                "id": track["id"],
                "track_name": track["name"],
                "artist": track["artists"][0]["name"],
                "artist_uri": track["artists"][0]["uri"],
                "album_uri": track["album"]["uri"],
                "album": track["album"]["name"],
                "release_date": track["album"]["release_date"],
                "popularity": track["popularity"],
                "explicit": track["explicit"]
            }
            # append newly flattened observation into flattened tracks list
            flattened_tracks.append(flattened_track)
        except:
            continue
        
    return flattened_tracks

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
    for i in range(0, len(track_ids)):
        # get batch of audio features for each chunk of 100
        audio_features_item = sp.audio_features(track_ids[i])
        # add batch to audio features
        audio_features += audio_features_item
    # turn audio features into a df
    audio_features_df = pd.DataFrame(audio_features)
    # drop columns we dont need
    audio_features_df = audio_features_df.drop(columns=['type', 'uri', 'track_href', 'analysis_url'])
    # return df
    return audio_features_df
    

def get_genres(sp, df):
    """
    Retrieves the user's saved or liked tracks from their profile and returns a list of JSON Track Objects.
    :param sp: a spotipy.Spotify object with an access token for the user.
    :return tracks: a list of returned JSON Track Objects from the spotipy api call.
    """
    # Use List Comprehension to get List of all track ids
    artist_uris = [track for track in df['artist_uri']]
    # set list for audio features
    genres = []
    # iterate through list of track ids 100 at a time to account for api call limit
    for uri in artist_uris:
        # get batch of audio features for each chunk of 100
        artist = sp.artist(uri)
        try:# add batch to audio features
            genres.append({'artist_uri': artist['uri'], 'genres': artist['genres']})
        except:
            genres.append({'artist_uri': artist['uri'], 'genres': []})
    df_genres = pd.DataFrame(genres)
    df = pd.merge(df,df_genres, on='artist_uri', how='left')
    return df


def prepare_tracks_for_model(sp, tracks_to_flat):
    
    tracks_for_model = pd.DataFrame(flatten_tracks(tracks_to_flat))
    tracks_for_model['explicit'] = tracks_for_model['explicit'].apply(lambda x: 1 if x==True else 0)
    tracks_for_model['release_year'] = pd.to_datetime(tracks_for_model['release_date'],errors='coerce').dt.year
    tracks_for_model['release_year']=tracks_for_model['release_year'].astype(int)
    audio_for_model = get_track_audio_features(sp, tracks_for_model)
    tracks_for_model = pd.merge(audio_for_model, tracks_for_model, on='id', how='right')
    tracks_for_model = get_genres(sp, tracks_for_model)
    tracks_for_model = tracks_for_model[['id', 'track_name', 'artist', 'artist_uri', 'album_uri', 'album',
   'release_date', 'popularity', 'explicit', 'danceability', 'energy', 'key', 
   'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 
   'liveness', 'valence', 'tempo', 'duration_ms', 'time_signature', 'release_year','genres']]
    tracks_for_model = tracks_for_model.drop_duplicates(subset='id')
    
    return tracks_for_model
