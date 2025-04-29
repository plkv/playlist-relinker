from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import openai
import os

app = Flask(__name__)
CORS(app, origins=["https://exuberant-managers-615414.framer.app"])  # Разрешаем только Framer-домен

# Spotify API constants
SPOTIFY_CLIENT_ID = "e727213173e141f482270557f6d11e26"
SPOTIFY_CLIENT_SECRET = "924f0275c3214841a33331d0959e2c4f"
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

# app.py (добавить после импорта и авторизации)
user_token = None  # Временно, на одного пользователя

@app.route("/token", methods=["POST"])
def save_token():
    global user_token
    data = request.get_json()
    user_token = data.get("token")
    print("✅ Saved token:", user_token)
    return jsonify({"status": "ok"})

access_token = None  # Глобальная переменная для хранения токена

@app.route("/token", methods=["POST"])
def store_token():
    global access_token
    data = request.get_json()
    access_token = data.get("token")
    print("✅ Access token received and stored")
    return jsonify({"status": "ok"})

playlist_data = {}

@app.route("/setlink", methods=["POST"])
def set_link():
    global access_token, playlist_data

    if not access_token:
        return "Not authorized", 401

    data = request.get_json()
    playlist_url = data.get("playlist_url")

    if not playlist_url:
        return "Missing playlist URL", 400

    # Извлечение playlist ID
    match = re.search(r"playlist/([a-zA-Z0-9]+)", playlist_url)
    if not match:
        return "Invalid playlist URL", 400

    playlist_id = match.group(1)

    # Запрос к Spotify
    headers = {"Authorization": f"Bearer {access_token}"}
    playlist_resp = requests.get(
        f"https://api.spotify.com/v1/playlists/{playlist_id}", headers=headers
    )

    if playlist_resp.status_code != 200:
        print("❌ Spotify error:", playlist_resp.text)
        return "Spotify error", 500

    playlist_json = playlist_resp.json()

    tracks = []
    for item in playlist_json["tracks"]["items"]:
        name = item["track"]["name"]
        artist = item["track"]["artists"][0]["name"]
        tracks.append({"original": f"{artist} - {name}", "found": None})

    playlist_data = {
        "playlist_name": "♻️ " + playlist_json["name"],
        "playlist_url": playlist_url,
        "total_count": len(tracks),
        "found_count": 0,
        "not_found_count": len(tracks),
        "tracks": tracks,
    }

    return jsonify({"status": "ok"})
@app.route("/results", methods=["GET"])
def get_results():
    return jsonify(playlist_data)
@app.route("/search-tracks", methods=["POST"])
def search_tracks():
    global access_token, playlist_data

    if not access_token:
        return "Not authorized", 401

    headers = {"Authorization": f"Bearer {access_token}"}

    new_tracks = []
    found = 0
    not_found = 0

    for track in playlist_data.get("tracks", []):
        original = track["original"]

        # Запрос к GPT
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Ты помогаешь найти треки в Spotify."},
                    {"role": "user", "content": f"Исправь название трека для поиска в Spotify: {original}"},
                ]
            )
            corrected = completion.choices[0].message["content"]
        except Exception as e:
            print(f"❌ GPT error: {e}")
            corrected = original

        # Поиск трека в Spotify
        query = corrected.strip()
        search_resp = requests.get(
            "https://api.spotify.com/v1/search",
            headers=headers,
            params={"q": query, "type": "track", "limit": 1}
        )

        if search_resp.status_code != 200:
            print(f"❌ Spotify search error: {search_resp.text}")
            new_tracks.append({"original": original, "found": None})
            not_found += 1
            continue

        results = search_resp.json()
        items = results.get("tracks", {}).get("items", [])

        if items:
            track_name = items[0]["name"]
            artist_name = items[0]["artists"][0]["name"]
            new_tracks.append({"original": original, "found": f"{artist_name} - {track_name}"})
            found += 1
        else:
            new_tracks.append({"original": original, "found": None})
            not_found += 1

    # Обновляем результаты
    playlist_data["tracks"] = new_tracks
    playlist_data["found_count"] = found
    playlist_data["not_found_count"] = not_found

    return jsonify({"status": "ok"})

