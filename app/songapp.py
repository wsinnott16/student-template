from flask import Flask, render_template
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/songSearch/title/<>")
def getSongs():
    dataList = ["top_tracks_2023.json", "top_tracks_2024.json", "top_tracks_2026.json"]
    for list in dataList:
        for item in list.items():
            