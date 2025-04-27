from flask import Flask, render_template, request, redirect, session, url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

CLIENT_ID = 'e727213173e141f482270557f6d11e26'
CLIENT_SECRET = '924f0275c3214841a33331d0959e2c4f'
REDIRECT_URI = 'https://playlist-relinker.onrender.com/callback'

SCOPE = 'playlist-read-private playlist-read-collaborative playlist-modify-public playlist-modify-private'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                             client_secret=CLIENT_SECRET,
                             redirect_uri=REDIRECT_URI,
                             scope=SCOPE)
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                             client_secret=CLIENT_SECRET,
                             redirect_uri=REDIRECT_URI,
                             scope=SCOPE)
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    return redirect(url_for('link'))

@app.route('/link', methods=['GET', 'POST'])
def link():
    token_info = session.get('token_info', None)
    if not token_info:
        return redirect(url_for('login'))

    if request.method == 'POST':
        playlist_url = request.form['playlist_url']
        session['playlist_url'] = playlist_url
        return redirect(url_for('relink'))

    return render_template('link.html')

@app.route('/relink')
def relink():
    token_info = session.get('token_info', None)
    playlist_url = session.get('playlist_url', None)

    if not token_info or not playlist_url:
        return redirect(url_for('home'))

    sp = spotipy.Spotify(auth=token_info['access_token'])

    try:
        playlist_id = playlist_url.split("/")[-1].split("?")[0]
        original_playlist = sp.playlist(playlist_id)
        tracks_data = sp.playlist_tracks(playlist_id)
        tracks = tracks_data['items']

        found_tracks = []
        not_found_tracks = []
        report_tracks = []

        for item in tracks:
            track = item['track']
            if track:
                original_track_name = track['name']
                original_artist_name = track['artists'][0]['name']
                original_query = f"{original_track_name} {original_artist_name}"

                search_result = sp.search(q=original_query, type="track", limit=1)
                if search_result['tracks']['items']:
                    found_track = search_result['tracks']['items'][0]
                    found_track_name = found_track['name']
                    found_artist_name = found_track['artists'][0]['name']
                    found_tracks.append(found_track['id'])
                    report_tracks.append({
                        'status': 'found',
                        'original': f"{original_artist_name} – {original_track_name}",
                        'found': f"{found_artist_name} – {found_track_name}"
                    })
                else:
                    not_found_tracks.append(original_query)
                    report_tracks.append({
                        'status': 'not_found',
                        'original': f"{original_artist_name} – {original_track_name}",
                        'found': None
                    })

        user_id = sp.current_user()['id']

        new_playlist = sp.user_playlist_create(
            user=user_id,
            name=f"♻️ {original_playlist['name']}",
            public=True
        )

        if found_tracks:
            sp.playlist_add_items(playlist_id=new_playlist['id'], items=found_tracks)

        return render_template('relink.html', 
                               playlist_name=new_playlist['name'],
                               playlist_url=new_playlist['external_urls']['spotify'],
                               total=len(report_tracks),
                               found=len(found_tracks),
                               not_found=len(not_found_tracks),
                               report_tracks=report_tracks)

    except Exception as e:
        return render_template('relink.html', error=str(e))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
