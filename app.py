import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv
import pickle
import pandas as pd
import  streamlit.components.v1 as component
load_dotenv("./.env")

client_id = os.environ.get("SPOTIFY_CLIENT_ID")
client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id, client_secret), requests_timeout=45)

st.title("Spotify Dashboard")

def load(filename = "filename.pickle"): 
    try: 
        with open(filename, "rb") as f: 
            return pickle.load(f) 

    except FileNotFoundError: 
        print("File not found!")

kmeans = load("kmeans4000.pickle")
scaler = load("scaler.pickle")

def getClusterIds(_df):
    cluster_ids = kmeans.predict(_df)
    return cluster_ids

# Final UI:
# - Input: song name
inpt = st.text_input("Enter song name: ")

if len(inpt) > 0:
    # - Search for song in Spotify
    results = sp.search(q=inpt, limit=1)
    # - Get song id
    song_id = results["tracks"]["items"][0]["id"]
    # - Get song features
    inpt_features = sp.audio_features(song_id)
    df = pd.DataFrame(inpt_features)[["danceability", "energy", "loudness", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo"]]
    X_normalized = scaler.transform(df)
    # - Get cluster id
    inpt_cluster = getClusterIds(X_normalized)
    # - Get songs in cluster
    df2 = pd.read_csv("features_clustered.csv")
    songs_in_cluster = df2[df2["cluster_id"] == inpt_cluster[0]]["id"].tolist()
    song_names = sp.tracks(songs_in_cluster[0:10])["tracks"]
    song_names_legible = [i["name"] + ' - ' + i["artists"][0]["name"] for i in song_names]
    # - Display input song
    st.write("Your song:")
    component.iframe('https://open.spotify.com/embed/track/' + song_id)
    st.write("Recommended song:")
    component.iframe('https://open.spotify.com/embed/track/' + songs_in_cluster[0])
    isOk = st.text_input("Do you like it? (y/n) ")
    if isOk.lower() == "y": 
        st.write("Great!")
    elif isOk.lower() == "n": 
        st.write("Ok, let's see what else we have!")
        for i in range(1, 10):
            component.iframe('https://open.spotify.com/embed/track/' + songs_in_cluster[i])

