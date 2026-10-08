from flask import Flask, render_template
from flask import Flask, jsonify
import json

app = Flask(__name__)

@app.route("/songSearch/title/<search_title>")
def getSongs(search_title):
    songs = []
    dataList = ["top_tracks_2023.json", "top_tracks_2024.json", "top_tracks_2026.json"]
    for list in dataList:
        with open(list, 'r') as f:
            data = json.load(f)
        for title, artists, popularity, explicit, url, duration_mins, genres in data.items():
            if search_title in title:
                songList = []
                titledict = {title}
                artistsdict = {artists}
                popularitydict = {popularity}
                explicitdict = {explicit}
                urldict = {url}
                duration_minsdict = {duration_mins}
                genresdict = {genres}
                songList.append(titledict, artistsdict, popularitydict, explicitdict, urldict, 
                                duration_minsdict, genresdict)
                songs.append(songList)
    return jsonify(songs)