from flask import Flask, render_template, request
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os

app = Flask(__name__)

CLIENT_ID = 'e727213173e141f482270557f6d11e26'
CLIENT_SECRET = '924f0275c3214841a33331d0959e2c4f'

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
))

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ''
    if request.method == 'POST':
        playlist_url = request.form['playlist_url']
        try:
            playlist_id = playlist_url.split("/")[-1].split("?")[0]
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

            message = f"✅ Найдено: {len(found_tracks)} треков. ❌ Не найдено: {len(not_found_tracks)} треков."

        except Exception as e:
            message = f"Ошибка: {str(e)}"

    return render_template('index.html', message=message)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
