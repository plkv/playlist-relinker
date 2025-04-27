from flask import Flask, render_template, request
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)

# 🔥 Твои данные
CLIENT_ID = 'e727213173e141f482270557f6d11e26'
CLIENT_SECRET = '924f0275c3214841a33331d0959e2c4f'
REDIRECT_URI = 'https://localhost:8888/callback'

# Авторизация для Spotify API
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="playlist-read-private playlist-read-collaborative playlist-modify-public playlist-modify-private"
))

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ''
    if request.method == 'POST':
        playlist_url = request.form['playlist_url']
        try:
            # Извлекаем ID плейлиста из URL
            playlist_id = playlist_url.split("/")[-1].split("?")[0]

            # Получаем все треки из старого плейлиста
            results = sp.playlist_tracks(playlist_id)
            tracks = results['items']

            found_tracks = []
            not_found_tracks = []

            for item in tracks:
                track = item['track']
                if track:
                    track_name = track['name']
                    artist_name = track['artists'][0]['name']
                    query = f"{track_name} {artist_name}"

                    search_result = sp.search(q=query, type="track", limit=1)
                    if search_result['tracks']['items']:
                        found_tracks.append(search_result['tracks']['items'][0]['id'])
                    else:
                        not_found_tracks.append(query)

            # Создаем новый плейлист
            user_id = sp.current_user()["id"]
            new_playlist = sp.user_playlist_create(user=user_id, name="Offline to Online Playlist - Recovered", public=True, description="Converting old playlists based on offline mp3 files to online Spotify playlists")

            # Добавляем найденные треки
            if found_tracks:
                sp.playlist_add_items(playlist_id=new_playlist['id'], items=found_tracks)

            message = f"✅ Найдено и добавлено: {len(found_tracks)} треков. ❌ Не найдено: {len(not_found_tracks)} треков."

        except Exception as e:
            message = f"Ошибка: {str(e)}"

    return render_template('index.html', message=message)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
