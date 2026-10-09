import json
from functools import lru_cache
from pathlib import Path

from flask import Flask, jsonify, request

app = Flask(__name__)

DATA_DIR = Path(__file__).parent / "data"
YEARS = ["2023", "2024", "2026"]


@lru_cache(maxsize=1)
def load_tracks():
    """Read every year's file once and return all tracks as one list.
    Each track gets a 'year' field. Cached (restart to reload)."""
    tracks = []
    for year in YEARS:
        path = DATA_DIR / f"top_tracks_{year}.json"
        with open(path, "r", encoding="utf-8") as f:
            for track in json.load(f):
                track["year"] = year
                tracks.append(track)
    return tracks


def valid_fields(tracks):
    """Every field name that appears in the data."""
    return set().union(*(track.keys() for track in tracks))


def matches_search(track, search_by, search_terms):
    value = track.get(search_by, "")
    text = " ".join(value) if isinstance(value, list) else str(value)
    text_lower = text.lower()
    return all(term in text_lower for term in search_terms.lower().split())


def filter_tracks(tracks, search_by, search_terms, include_explicit):
    return [
        track for track in tracks
        if matches_search(track, search_by, search_terms)
        and (include_explicit or not track.get("explicit", False))
    ]


def sort_tracks(tracks, sort_by):
    return sorted(tracks, key=lambda track: track.get(sort_by, 0), reverse=True)


@app.route("/search", methods=["POST"])
def search():
    req = request.get_json(silent=True) or {}
    search_by = req.get("search-by", "title")
    sort_by = req.get("sort-by", "popularity")
    include_explicit = req.get("explicit", True)
    search_terms = req.get("search-bar", "")

    tracks = load_tracks()
    fields = valid_fields(tracks)
    if search_by not in fields:
        return jsonify(error=f"search-by must be one of {sorted(fields)}"), 400
    if sort_by not in fields:
        return jsonify(error=f"sort-by must be one of {sorted(fields)}"), 400

    results = filter_tracks(tracks, search_by, search_terms, include_explicit)
    return jsonify(sort_tracks(results, sort_by))