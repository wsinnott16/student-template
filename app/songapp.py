import json
from functools import lru_cache
from pathlib import Path
 
from flask import Flask, jsonify, request, render_template
 
app = Flask(__name__)

#-------------------------------
# This is for loading the top track files 
#-------------------------------
# it is outside of app, at the project root. 
DATA_DIR = Path(__file__).parent.parent 
YEARS = ["2023", "2024", "2026"]
@lru_cache(maxsize=1)
def load_tracks():
    """Read every year's file once and return all tracks as one list.
 
    Each track gets a 'year' field recording which file it came from.
    Cached, so files are not re-read on every request (restart to reload).
    """
    tracks = []
    for year in YEARS:
        path = DATA_DIR / f"top_tracks_{year}.json"
        with open(path, "r", encoding="utf-8") as f:
            for track in json.load(f):
                track["year"] = year
                tracks.append(track)
    return tracks

def valid_fields(tracks):
    """
    Every field name that appears in the data (used to validate requests by user)
    uses key to define the parameters, values change. 
    """
    return set().union(*(track.keys()for track in tracks))


#-------------------------------------------
# This is for the filtering of the song
#-------------------------------------------
def matches_search(track, search_by, search_terms):
    """
    The first parameter (button) and the second are joined into one string. 
    """
    value = track.get(search_by, "")
    text = " ".join(value) if isinstance(value, list) else str(value)
    words = text.lower().split(" ")

    return all(term in words for term in search_terms.lower().split(" "))


def filter_tracks(tracks, search_by, search_terms, include_explicit):
    '''
    Keeps track with a list of the matches based on the search and considers
    the explicit setting.
    '''

    return [track for track in tracks if matches_search(track, search_by, search_terms) and 
            (include_explicit or not track.get("explicit", False))]


def sort_tracks(tracks, sort_by):   
    """Return a new list of the sorted elements with the sort by"""
    return sorted(tracks, key=lambda track: track[sort_by], reverse = True)



# This is the app route, so that it can jsonify and address the result.
@app.route("/")
def index():
    return render_template("songsearch.html")

@app.route("/search", methods=["POST"])
def search():
    # 1. Read the request, with defaults for anything missing.
    req = request.get_json(silent=True) or {}
    search_by = req.get("search-by", "title")
    sort_by = req.get("sort-by", "popularity")
    include_explicit = req.get("explicit", True)
    search_terms = req.get("search-bar", "")
 
    # 2. Validate the field names so a bad value returns a clear error.
    tracks = load_tracks()
    fields = valid_fields(tracks)
    if search_by not in fields:
        return jsonify(error=f"search-by must be one of {sorted(fields)}"), 400
    if sort_by not in fields:
        return jsonify(error=f"sort-by must be one of {sorted(fields)}"), 400
 
    # 3. Filter, then sort.
    results = filter_tracks(tracks, search_by, search_terms, include_explicit)
    return jsonify(sort_tracks(results, sort_by))
 