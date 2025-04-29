from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import openai

app = Flask(__name__)
CORS(app)  # разрешить запросы с любых доменов

# Spotify Auth
SPOTIFY_CLIENT_ID = "e727213173e141f482270557f6d11e26"
SPOTIFY_CLIENT_SECRET = "924f0275c3214841a33331d00959e2c4f"
REDIRECT_URI = "https://exuberant-managers-615414.framer.app/setlink"

# GPT
openai.api_key = os.getenv("OPENAI_API_KEY")

# Хранилище мок-результатов (в реальности можно заменить на Redis, сессии и т.д.)
results_data = {}

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

    return jsonify(response.json())

@app.route("/setlink", methods=["POST"])
def set_link():
    data = request.get_json()
    playlist_url = data.get("playlist_url")

    # здесь ты можешь сохранить ссылку или сразу что-то обработать
    results_data["playlist_name"] = "My Playlist"
    results_data["playlist_url"] = playlist_url
    results_data["tracks"] = [
        {
            "original": "Daft Punk – Harder, Better, Faster, Stronger",
            "found": "Daft Punk – Harder Better Faster Stronger (MP3)"
        },
        {
            "original": "Unknown Artist – Random Track",
            "found": None
        }
    ]
    results_data["total_count"] = 2
    results_data["found_count"] = 1
    results_data["not_found_count"] = 1

    return jsonify({"success": True})

@app.route("/results", methods=["GET"])
def get_results():
    return jsonify(results_data)

if __name__ == "__main__":
    app.run(debug=True)
