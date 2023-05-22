# SoundSuggestionEngine

## Table of Contents

- Background
- Problem Statement
- Data Dictionary
- Brief Summary of Analysis
- Conclusions and Recommendations
- File Structure
- Sources
- Powerpoint Presentation

## Background:
Music is a universal language, but its nuances can often be subjective and hard to translate into objective, quantifiable data. In recent years, the ability to represent song data numerically through different audio track features and measurements has opened up a new dimension for music exploration. By creating a song recommendation engine based on given audio track features and track metadata, we can potentially make music more accessible and enjoyable for all.

## Problem Statement:
Our startup aims to create a product that leverages Spotify's Web APIs to translate tracks, artists, and genres into vectors of audio track features. Our primary goal is to provide music recommendations, but we envision this as just the starting point. Ultimately, our application will evolve to take user identity-agnostic music recommendation data, create a network based on submissions over time, and track which track audio features are most successful. This could provide valuable insights for those aspiring to create their own music, giving them a sense of what works best.
___
<h1>Data Dictionary</h1>

|Feature|Type|Description|
|:---|:---:|:---|
|**id**|*object*|Spotify Web API Track ID|
|**track_name**|*object*|Name of Track|
|**artist**|*object*|Name of Artist|
|**artist_id**|*object*|Spotify Web API Artist ID|
|**album_id**|*object*|Spotify Web API Album ID|
|**album**|*object*|Spotify Web API Album ID|
|**release_date**|*object*|Date Track was released|
|**playlist_name**|*object*|Name of the Playlist the track was retrieved from|
|**popularity**|*int*|The popularity of a track is a value between 0 and 100, with 100 being the most popular. The popularity is calculated by algorithm and is based, in the most part, on the total number of plays the track has had and how recent those plays are.|
|**explicit**|*boolean*|Whether or not the track has explicit lyrics ( true = yes it does; false = no it does not OR unknown).|
|**user_liked**|*int*|Feature created to capture whether a not a song was pulled from the Liked Songs Playlist|
|**danceability**|*float*|Danceability describes how suitable a track is for dancing based on a combination of musical elements including tempo, rhythm stability, beat strength, and overall regularity. A value of 0.0 is least danceable and 1.0 is most danceable.|
|**energy**|*float*|Energy is a measure from 0.0 to 1.0 and represents a perceptual measure of intensity and activity. Typically, energetic tracks feel fast, loud, and noisy. For example, death metal has high energy, while a Bach prelude scores low on the scale. Perceptual features contributing to this attribute include dynamic range, perceived loudness, timbre, onset rate, and general entropy.|
|**key**|*int*|The key the track is in. Integers map to pitches using standard [Pitch Class notation](https://en.wikipedia.org/wiki/Pitch_class). E.g. 0 = C, 1 = C♯/D♭, 2 = D, and so on. If no key was detected, the value is -1.
|**loudness**|*float*|The overall loudness of a track in decibels (dB). Loudness values are averaged across the entire track and are useful for comparing relative loudness of tracks. Loudness is the quality of a sound that is the primary psychological correlate of physical strength (amplitude). Values typically range between -60 and 0 db.|
|**mode**|*int*|Mode indicates the modality (major or minor) of a track, the type of scale from which its melodic content is derived. Major is represented by 1 and minor is 0.|
|**speechiness**|*float*|Speechiness detects the presence of spoken words in a track. The more exclusively speech-like the recording (e.g. talk show, audio book, poetry), the closer to 1.0 the attribute value. Values above 0.66 describe tracks that are probably made entirely of spoken words. Values between 0.33 and 0.66 describe tracks that may contain both music and speech, either in sections or layered, including such cases as rap music. Values below 0.33 most likely represent music and other non-speech-like tracks.|
|**acousticness**|*float*|A confidence measure from 0.0 to 1.0 of whether the track is acoustic. 1.0 represents high confidence the track is acoustic.|
|**instrumentalness**|*float*|Predicts whether a track contains no vocals. "Ooh" and "aah" sounds are treated as instrumental in this context. Rap or spoken word tracks are clearly "vocal". The closer the instrumentalness value is to 1.0, the greater likelihood the track contains no vocal content. Values above 0.5 are intended to represent instrumental tracks, but confidence is higher as the value approaches 1.0.|
|**liveness**|*float*|Detects the presence of an audience in the recording. Higher liveness values represent an increased probability that the track was performed live. A value above 0.8 provides strong likelihood that the track is live.|
|**valence**|*float*|A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track. Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), while tracks with low valence sound more negative (e.g. sad, depressed, angry).
|**tempo**|*float*|The overall estimated tempo of a track in beats per minute (BPM). In musical terminology, tempo is the speed or pace of a given piece and derives directly from the average beat duration.|
|**duration_ms**|*int*|The duration of the track in milliseconds.|
|**time_signature**|*int*|An estimated time signature. The time signature (meter) is a notational convention to specify how many beats are in each bar (or measure). The time signature ranges from 3 to 7 indicating time signatures of "3/4", to "7/4".|

___

## Brief Summary of Analysis

### Data
The data used in this project was sourced from two locations: Spotify Web APIs and Kaggle. All data was structured, a mix of numerical Track Audio Features and Track Metadata (Artist, Album, Name, etc.) with little cleaning needed to be done. Data sourced from the Spotify Web APIs were pulled via two authorization protocols. The first and second attempts were authorized via a Authorization Code flow, being granted access to a given users profile information, the third attempt was via a server-server authentication which was pulling information only from Spotify itself. The Kaggle dataset (listed below) was utilized to save time and effort to both expand the number of observations for our models, but also provide us the opportunity to increase dimensionality. 

## Methodology

### Data Preprocessing
As mentioned in Data, little cleaning was needed from either of the data sources as we needed to handle exceptions during the data gathering process leading to most null values to be skipped entirely from the collection phase. We did however have to normalize all of our numerical track audio features to be on the same scale for our KMeans clustering models. Principle Component Analysis was also utilized to best understand the potential number of clusters needed to cover the highest percentage of variance in the data. As mentioned below, PCA gave us our first hints that the data didnt have enough dimensions to single out any solid clusters.

### Feature Engineering
To increase dimensionality, boolean and datetime features were manipulated such as changing explicit (profanity in this instance) from its Boolean values to their numerical counterparts and release date to a shortened release year. When we were able to collect genres per track, we attempted to one hot encode the unique sub genres however due to the size of the unique list of genres (4407) we hit computational and memory issues when trying to process.

In the early stages of the project, when we were working on classifying musical taste which would eventually be replaced by the mean vector calculation, we not only standard scaled the data but also used polynomial features to create versions of features that were themselves squared (a*a) and interactions between other variables (a*b)

### Model Selection
We chose K-Means as our unsupervised clustering model for its scalability, simplicity, ability to work well with multi-dimensional data, interpretability, and speed. K-Means is a centroid based clustering algorithm which gives it a linear scal with respect to O notation as well as doesn't require the computation of a full distance matrix between all paired points, simply the computation of distances between data points and cluster centroids. One noted drawback is the curse of dimensionality, in which when there are too many features, the distance between any two points in the feature space tends to become more uniform, reducing distinguishing boundaries.

Briefly, during the early stages of the project we also crafted two versions of classification model suites including RandomForestClassifier, LogisticRegression, ADABoostClassifier, BaggingClassifier, SVC trained on Scaled Data alone, and also on Scaled Data plus Polynomial Features. We ultimately didnt choose any NaiveBayes classifier models because the values weren't binary.

### Model Evaluation
For the K-Means clusters, we scored our performance using the silhouette score which acts as a measure of how well a given object lies within its cluster in relation to other clusters. Silhouette scores range between -1 and +1, -1 being the worst and +1 being the best. It was also used as a comparison tool for the different number of clusters we needed to include at model instantiation by comparing different scores and different n_cluster values. 

For the classification models, our main metric was accuracy because it was more important that, at the time, we classify the musical mean taste accurately as it was planned to be used as a method for identifying a given signal based on audio track features to generate song recommendations. We gathered other metrics as well for posterity including recall, precision, and f1 score

### Results
For the K-Means clusters, our best silhouette score was 0.22 but with only two clusters, while our best recommendation clustering model had a silhouette score of 0.101. In both instances our models were suffering from what I believe to be the opposite end of the spectrum of the Curse of Dimensionality. Sixteen different audio features weren't enough provide the model enough feature space to create separate enough clusters; there was a lot of overlap. If we had the computational power and memory to encode the different genres, we could test the high end of the spectrum and start to gauge an appropriate range of dimensions where distinct and dense clusters start to appear. Going forward we also want to try methods such as Density-Based Spatial Clustering of Applications with Noise for it's density based approach; could help classify outlier songs as well as unlike K-Means, it doesnt assume the clusters are convex, a higher range of cluster shape options. Also as seen from the different "grid search" attempts, the number of clusters is still relatively unknown which DBSCAN decides on based on the density of the data. This, however, is rooted in our ability to utilize genre effectively in the data.

For the different classification models, our baseline classification model was ~75% where the differentiator was explicit song interactions (songs the user directly actioned as liking), implict song interactions (songs they may have listened to), and general interactions (songs we dont know they have listened to but they have access too). In each version, StandardScaled v. StandarScaled & Polynomial Features, we were barely able to beat the baseline score. Our Best Model was a Logistic Regression model with a train and test accuracy of ~0.76.

## Conclusions and Recommendations
- The current limitations of our application are mainly due to data storage and processing limits. As we scale up, we need more robust solutions for handling larger data sets without crashing. Our next steps would be to use PyTorch and Databricks to leverage multiprocessing in preprocessing, modeling, and certain visualizations.
- For future enhancements, we recommend building a classification model for better generalizing genres to increase our data dimensionality as genres are not fixed and have a wide range of possibilities. 
- Our final Dataset has ~4400 unique genres. In order to prevent any kind of negative dimensionality impact to our overall dataset without losing out on the potential correlations of audio track feature vectors and different genres, we could train a classification model trained on track audio features, track metadata, artist metadata, and one hot encoded genres to classify a higher level group of genres and/or potentially try and cluster them as well. This would enable us to increase our feature set for further value, without falling prey to the curse of dimensionality.
- We would also like to create an SQL database to store not only the data we use for modeling and visualizing, but going forward we also want to store anonymous user submissions and queries for later metadata analyses. 
- We could capture the songs, genres, and or artists that users searched, the recommendations they were given, and add further functionality for them to select of the songs which they will like and capture that as explicit interactions. These submissions could later be used to expand our use case to the original intent of collaboritive filtering as well as tracking popularity of songs based in audio features over time.
- Lastly, implementing unit testing and error controls for the application would be beneficial for maintaining the application's reliability and robustness.

File Structure:
```
├── code
│   app
│   ├── v0
│   ├── app.py
│   ├── extended_library.pkl
│   ├── get_methods.py
│   ├── README.md
│   ├── recommend_library.csv
│   ├── requirements.txt
│   ├── user_session.py
│   ├── viz_model_methods.py
│   01_Get_User_Data.ipynb
│   02_Explore_User_Data.ipynb
│   03_Model_User_Data_v2.ipynb
│   get_tracks_methods.py
│   model_methods.py
├── data
│   ├── rec_library_full.csv ~ "https://myawsbucketdsi221.s3.us-east-2.amazonaws.com/rec_library_full.csv"
│   ├── model_scores.csv
│   ├── explicit_implicit_tracks.csv
├── README.md
├── ExecutiveSummary.md

```
## Sources

- Kaggle Dataset for Extended Track Library: https://www.kaggle.com/datasets/yamaerenay/spotify-dataset-19212020-600k-tracks/code?resource=download
- Spotify Web API: https://developer.spotify.com/documentation/web-api/
- Song Recommendation: https://towardsdatascience.com/how-to-build-a-simple-song-recommender-296fcbc8c85
- Streamlit Help: https://towardsdatascience.com/creating-multipage-applications-using-streamlit-efficiently-b58a58134030
- Streamlit Auth Best Practices: https://towardsdatascience.com/how-to-add-a-user-authentication-service-in-streamlit-a8b93bf02031
- Genre Classification: https://towardsdatascience.com/music-genre-prediction-with-spotifys-audio-features-8a2c81f1a22e
- Stack Overflow

## Powerpoint

https://docs.google.com/presentation/d/1bQwHWKesxgvy5Ed1mBkCgaSzfOdyco_vJhIsGkTJef8/edit?usp=sharing