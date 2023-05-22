from user import User
import get_methods
import viz_model_methods
import streamlit as st
import pandas as pd
import pickle
import plotly
import numpy as np
import spotipy.oauth2 as oauth2

# Set up the page
st.set_page_config(page_title="What's your Spotify Signal?", page_icon=":bar_chart:", layout="wide")



# Set up the sidebar
st.sidebar.title("Project Authors")
st.sidebar.info(
    "This application was created by [Chris Joyce](https://github.com/chrisJoyceDS)."
)

st.sidebar.title("GitHub Repository")
st.sidebar.info(
    "[Link to the public GitHub repository](https://github.com/chrisJoyceDS/spotify-signal)."
)

def onboarding():
    user = User()
    return user


def main():
    user = onboarding()
    st.title("Using Spotify App Data to Visualize your Signal")
    st.write("Problem Statement:")
    st.write("""Loaded to the gunwalls scuttle coxswain barque lateen sail Arr mutiny yo-ho-ho Shiver me timbers topgallant. Ahoy clap of thunder topmast Corsair hands yard heave to line Cat o'nine tails scourge of the seven seas. Rigging wherry dead men tell no tales chase guns hogshead execution dock tender coffer provost cable.""")
    st.write("""For this Web App to perform we will need you as a user to authenticate access to the Spotify API for your individual profile. Before you choose yes or no, please see what access we will be asking for below:""")
    items = ['user-library-read: Access your saved content.', 'user-top-read: Read your top artists and content.', 'playlist-read-private: Access your private playlists.', 'user-follow-read: Access your followers and who you are following.']
    for i, item in enumerate(items, start=1):
        st.write(f"{i}. {item}")
    st.write("If these permissions are okay, please click the Authenticate button below to get started.")
    
    if user.access_token is None:
        if st.button("Authenticate"):
            user.authenticate()
            st.write("Successfully authenticated with Spotify API.")
            st.write("To begin let's load your Saved Tracks and Tracks from Playlists you have Created and/or Actively Followed!")    
    else:
        pass
      
    while user.access_token is not None:
        saved_tracks = get_methods.handler(user, identifier='get_saved_tracks')
        st.dataframe(saved_tracks).head()
        st.write("Below is a representation of your Spotify Music Signal!")
        st.write("Each violin represents a distribution of a different track audio feature. Where the violin is wider represents more records of those values, and the line in the middle represents the median of a given distribution.")
        saved_fig = viz_model_methods.visualize_signal(saved_tracks)
        st.pyplot(saved_fig)
        st.write("Let's get you your first 10 song recommendations based on this signal!")
        song_recs_full, song_recs = viz_model_methods.song_recommendations(saved_tracks)
        st.dataframe(song_recs)
        st.write("Now let's see how if your signal continues to show up in these recommendations and compare!")
        rec_fig = viz_model_methods.visualize_signal(song_recs_full)
        st.pyplot(rec_fig)
    # while user.access_token is not None:
    #     st.write("Sample of Playlist Tracks Will Load Here")
    #     user_playlist_tracks = get_methods.handler(user, "get_user_playlist_tracks")
    #     st.dataframe(user_playlist_tracks.loc[:,['track_name','artist','album','release_date','danceability']].head())
    #     playlist_fig = data_viz_methods.visualize_signal(user_playlist_tracks)
    #     st.pyplot(playlist_fig)
    #     break

if __name__ == "__main__":
    main()