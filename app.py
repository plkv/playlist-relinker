from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import openai

app = Flask(__name__)
CORS(app)

# Константы Spotify
SPOTIFY_CLIENT_ID = "e727213173e141f482270557f6d11e26"
SPOTIFY_CLIENT_SECRET = "924f0275c3214841a33331d0959e2c4f"
REDIRECT_URI = "https://exuberant-managers-615414.framer.app/setlink"

# GPT API
import os
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

    if response.ok:
        return response.json()
    else:
        return {"error": "failed to exchange code"}, 400

@app.route("/fetch-tracks", methods=["POST"])
def fetch_tracks():
    data = request.get_json()
    url = data.get("url")
    token = data.get("access_token")

    # Пример получения треков из плейлиста (упрощённый)
    playlist_id = url.split("/")[-1].split("?")[0]
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks", headers=headers)

    if not response.ok:
        return {"error": "Spotify playlist fetch failed"}, 400

    items = response.json()["items"]
    raw_tracks = []
    for item in items:
        track = item["track"]
        name = f"{track['artists'][0]['name']} - {track['name']}"
        raw_tracks.append(name)

    # Используем GPT для уточнения треков
    matched_tracks = []
    for i, track in enumerate(raw_tracks):
        prompt = f"Найди точное название этого трека для Spotify: \"{track}\". Ответ: только имя исполнителя и название."
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            matched = response.choices[0].message["content"].strip()
        except Exception:
            matched = track  # fallback

        matched_tracks.append({
            "id": str(i + 1),
            "original": track,
            "matched": matched
        })

    return jsonify({"tracks": matched_tracks})

@app.route("/select", methods=["POST"])
def select():
    data = request.get_json()
    print("User selected track:", data)
    return jsonify({"status": "ok"})

@app.route("/")
def health():
    return jsonify({"status": "running"})
