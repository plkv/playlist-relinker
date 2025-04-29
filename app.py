from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import openai

app = Flask(__name__)

# Разрешаем CORS только для сайта во Framer
CORS(app, origins=["https://exuberant-managers-615414.framer.app"])

# Константы Spotify
SPOTIFY_CLIENT_ID = "e727213173e141f482270557f6d11e26"
SPOTIFY_CLIENT_SECRET = "924f0275c3214841a333310d0959e2c4"
REDIRECT_URI = "https://exuberant-managers-615414.framer.app/setlink"

# GPT API ключ
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/spotify/auth", methods=["POST"])
def exchange_code():
    data = request.get_json()
    code = data.get("code")

    response = requests.post("https://accounts.spotify.com/api/token", data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET
    })

    return jsonify(response.json()), response.status_code

@app.route("/setlink", methods=["POST"])
def handle_playlist_link():
    data = request.get_json()
    playlist_url = data.get("playlist_url")
    
    # Заглушка: здесь можно вставить обработку ссылки и вызов GPT/Spotify API
    if not playlist_url or "spotify.com/playlist/" not in playlist_url:
        return "Invalid playlist URL", 400

    # Например, просто вернуть ok
    return jsonify({"status": "ok", "message": "Playlist received"})
