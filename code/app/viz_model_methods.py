import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objs as go
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from scipy.spatial.distance import cdist
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA
import pickle
import numpy as np

######################################################################################################
# Data Vizualization Methods
######################################################################################################
def visualize_signal(df):
    # Select the numerical features you want to display
    features = ['danceability', 'energy', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence']

    # Create a list of colors for each violin
    colors = ['blue', 'orange', 'green', 'red', 'purple', 'gray', 'pink']

    # Create the violin plot with a separate plot for each feature
    fig, ax = plt.subplots(figsize=(12, 8))
    handles = []
    for i, feature in enumerate(features):
        ax.violinplot(dataset=df[feature], positions=[i], showmeans=False, showmedians=True, widths=0.8)
        handle = plt.Rectangle((0,0),1,1, color=colors[i], label=feature)
        handles.append(handle)

    # Add x-axis and y-axis labels
    ax.set_xlabel('Features')
    ax.set_ylabel('Values')
    ax.set_title('Distribution of Similar Ranged Audio Features from Gathered Songs')
    # Set the x-tick labels to be the feature names
    ax.set_xticks(range(len(features)))
    ax.set_xticklabels(features)
    
    # Add gridlines
    ax.grid(axis='y', linestyle='--', alpha=0.6)

    # Add a legend for the different colors
    ax.legend(handles=handles, bbox_to_anchor=(1.02, 1), loc='upper left')

    return fig


######################################################################################################
# Model Methods
######################################################################################################


# Based off Amol Mavuduru's mean vector function from:
# https://towardsdatascience.com/how-to-build-an-amazing-music-recommendation-system-4cce2719a572

def get_mean_vector(df):
    """
    This function is designed to take in a dataframe of track audio features and create the mean
    of a song matrix made up of the individual track features.
    :param df: a pandas dataframe of individual track and its audio features
    :return mean_vector: a song matrix mean vector to highlight a user's music taste signal
    """
    # set an empty list for each tracks audio feature values
    song_vectors = []
    # iterate through the rows of the given dataframe
    for index, row in df.iterrows():
        # append track audio feature values to song vectors list
        song_vectors.append(row.values)
    # create a matrix/np array out of song vectors list
    song_matrix = np.array(list(song_vectors))
    # calculate the mean of the song_matrix
    mean_vector = np.mean(song_matrix, axis=0)
    # return song vector
    return mean_vector



def song_recommendations(df):
    # pull in rec library
    recommend_library = pd.read_csv("https://myawsbucketdsi221.s3.us-east-2.amazonaws.com/rec_library_full.csv")
    # pull in pipeline from pickle
    with open('extended_library.pkl', 'rb') as f:
        pipeline = pickle.load(f)
    if df['release_year'].isnull().sum() > 0:
        df.dropna(axis=0, inplace=True)
    # scaler for data transformation previousl fitted 
    scaler = pipeline.steps[0][1]
    # num columns that model was trained on
    num_columns = df.select_dtypes(np.number).columns
    # calculate mean_vector to isolate a user's signal
    mean_vector = get_mean_vector(df[num_columns])
    # scale recommendation library
    scaled_data = scaler.transform(recommend_library[num_columns])
    # scale mean_vector and reshape to 2D Vector
    scaled_song_center = scaler.transform(mean_vector.reshape(1,-1))
    # calculate distances between the song center and the track recommendation library
    distances = cdist(scaled_song_center, scaled_data, 'cosine')
    # np.argsort(distances) computes the indices that would sort distances in asc order, returns a np array with the same shape
    # [:, :10] slices the np array to include only the first 10 columns of each row, effectively grabbing the 10 nearest neighbors
    # [0] selects the first row of the sliced np array
    # finally we convert it to a list all to get us the indices of the song library that make good recommendations
    index = list(np.argsort(distances)[:, :10][0])
    recommended_songs_full = recommend_library.iloc[index]
    recommended_songs = recommended_songs_full[['track_name','artist','release_year']]
    return recommended_songs_full, recommended_songs
