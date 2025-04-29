from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import openai
import os

app = Flask(__name__)
CORS(app, origins=["https://exuberant-managers-615414.framer.app"])  # Разрешаем только Framer-домен

# Spotify API constants
SPOTIFY_CLIENT_ID = "e727213173e141f482270557f6d11e26"
SPOTIFY_CLIENT_SECRET = "924f0275c231481a333310d0959e2c4f"
REDIRECT_URI = "https://exuberant-managers-615414.framer.app/setlink"

# GPT API
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
        "client_secret": SPOTIFY_CLIENT_SECRET,
    })

    return jsonify(response.json()), response.status_code

@app.route("/setlink", methods=["POST"])
def handle_setlink():
    data = request.get_json()
    playlist_url = data.get("playlist_url")

    # Временно: просто логируем
    print("Received playlist URL:", playlist_url)

    # Тут можно вставить логику обработки ссылки и редирект/ответ
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(debug=True)
