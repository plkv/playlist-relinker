from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)  # Разрешает CORS для всех доменов

# Spotify client credentials
SPOTIFY_CLIENT_ID = "e727213173e141f482270557f6d11e26"
SPOTIFY_CLIENT_SECRET = "924f0275c3214841a33331d0959e2c4f"
REDIRECT_URI = "https://exuberant-managers-615414.framer.app/setlink"

# Хранилище для результатов (в памяти, только временно)
latest_result = {}

@app.route("/spotify/auth", methods=["POST"])
def exchange_code():
    data = request.get_json()
    code = data.get("code")

    response = requests.post("https://accounts.spotify.com/api/token", data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET,
    })

    return jsonify(response.json()), response.status_code

@app.route("/setlink", methods=["POST"])
def setlink():
    global latest_result
    data = request.get_json()
    playlist_url = data.get("playlist_url")

    if not playlist_url or "open.spotify.com/playlist/" not in playlist_url:
        return "Invalid Spotify playlist URL", 400

    # Сохраняем заглушку в память
    latest_result = {
        "found_count": 0,
        "not_found_count": 0,
        "total_count": 0,
        "playlist_name": "Untitled Playlist",
        "playlist_url": playlist_url,
        "tracks": []
    }

    return "", 200

@app.route("/results", methods=["GET"])
def get_results():
    global latest_result
    if not latest_result:
        return jsonify({
            "error": "No playlist data available"
        }), 404

    return jsonify(latest_result)
