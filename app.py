from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

SPOTIFY_CLIENT_ID = "e727213173e141f482270557f6d11e26"
SPOTIFY_CLIENT_SECRET = "924f0275c321481a333310d0959e2c4f"
REDIRECT_URI = "https://exuberant-managers-615414.framer.app/setlink"

# Временное хранилище для данных результатов
latest_results = {}

def get_token():
    response = requests.post("https://accounts.spotify.com/api/token", data={
        "grant_type": "client_credentials",
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET
    })

    return response.json().get("access_token")

@app.route("/setlink", methods=["POST"])
def handle_setlink():
    global latest_results

    data = request.get_json()
    playlist_url = data.get("playlist_url")
    if not playlist_url:
        return "Missing playlist_url", 400

    # Извлечение ID
    if "playlist/" not in playlist_url:
        return "Invalid Spotify playlist URL", 400

    playlist_id = playlist_url.split("playlist/")[1].split("?")[0]

    # Получение access token
    token = get_token()
    if not token:
        return "Failed to authorize with Spotify", 500

    # Получение данных плейлиста
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"https://api.spotify.com/v1/playlists/{playlist_id}", headers=headers)
    if r.status_code != 200:
        return f"Spotify API error: {r.status_code}", 500

    raw = r.json()
    name = raw["name"]
    items = raw["tracks"]["items"]

    tracks = []
    for item in items:
        try:
            track = item["track"]
            original = f"{track['name']} — {track['artists'][0]['name']}"
            tracks.append({
                "original": original,
                "found": original  # пока просто возвращаем оригинал как найденный
            })
        except Exception:
            continue

    latest_results = {
        "playlist_name": f"♻️ {name}",
        "playlist_url": playlist_url,
        "total_count": len(tracks),
        "found_count": len(tracks),
        "not_found_count": 0,
        "tracks": tracks
    }

    return jsonify({"status": "ok"})

@app.route("/results", methods=["GET"])
def handle_results():
    return jsonify(latest_results or {
        "playlist_name": "",
        "playlist_url": "",
        "total_count": 0,
        "found_count": 0,
        "not_found_count": 0,
        "tracks": []
    })

if __name__ == "__main__":
    app.run()
