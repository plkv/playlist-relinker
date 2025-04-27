from flask import Flask, render_template, request, redirect, session, url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import re

app = Flask(__name__)
app.secret_key = os.urandom(24)

CLIENT_ID = 'e727213173e141f482270557f6d11e26'
CLIENT_SECRET = '924f0275c3214841a33331d0959e2c4f'
REDIRECT_URI = 'https://playlist-relinker.onrender.com/callback'
SCOPE = 'playlist-read-private playlist-read-collaborative playlist-modify-public playlist-modify-private'

# ======= Utility Functions =======

def normalize(text):
    text = text.lower()
    text = re.sub(r'\(.*?\)', '', text)  # Remove anything in parentheses
    text = re.sub(r'[^a-z0-9\s]', '', text)  # Remove special characters
    text = re.sub(r'\s+', ' ', text)  # Normalize spaces
    return text.strip()

def normalize_artist(text):
    text = text.lower()
    text = text.replace('feat.', ',')
    text = text.replace('ft.', ',')
    text = text.replace('&', ',')
    text = text.replace('and', ',')
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r',+', ',', text)
    text = text.replace(' ,', ',').replace(', ', ',')
    text = text.strip()
    return text

def artist_list(text):
    text = normalize_artist(text)
    return [normalize(artist) for artist in text.split(',') if artist]

def has_common_artist(original_artists, found_artists):
    return any(artist in found_artists for artist in original_artists)

def is_similar_name(name1, name2):
    n1 = normalize(name1)
    n2 = normalize(name2)
    return n1 in n2 or n2 in n1

# ======= Routes =======

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

@app.route('/relink', methods=['GET', 'POST'])
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
        report_tracks = []

        for item in tracks:
            track = item['track']
            if not track:
                continue

            original_track_name = track['name']
            original_artist_name = track['artists'][0]['name']
            original_artists = artist_list(original_artist_name)

            query = f"{original_track_name} {original_artist_name}"
            search_result = sp.search(q=query, type="track", limit=5)

            best_match = None

            if search_result['tracks']['items']:
                for candidate in search_result['tracks']['items']:
                    candidate_name = candidate['name']
                    candidate_artists = ', '.join(a['name'] for a in candidate['artists'])
                    found_artists_list = artist_list(candidate_artists)

                    if is_similar_name(candidate_name, original_track_name) and has_common_artist(original_artists, found_artists_list):
                        best_match = candidate
                        break

            # Fallback: search only by track name if no match
            if not best_match:
                fallback_query = f"{original_track_name}"
                fallback_result = sp.search(q=fallback_query, type="track", limit=5)

                for candidate in fallback_result['tracks']['items']:
                    candidate_name = candidate['name']
                    candidate_artists = ', '.join(a['name'] for a in candidate['artists'])
                    found_artists_list = artist_list(candidate_artists)

                    if is_similar_name(candidate_name, original_track_name) and has_common_artist(original_artists, found_artists_list):
                        best_match = candidate
                        break

            # Add result only once
            if best_match:
                found_tracks.append(best_match['id'])
                report_tracks.append({
                    'status': 'found',
                    'original': f"{original_artist_name} – {original_track_name}",
                    'found': f"{best_match['artists'][0]['name']} – {best_match['name']}"
                })
            else:
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
                               playlist_spotify_uri=new_playlist['uri'],
                               total=len(report_tracks),
                               found=len([t for t in report_tracks if t['status'] == 'found']),
                               not_found=len([t for t in report_tracks if t['status'] == 'not_found']),
                               report_tracks=report_tracks)

    except Exception as e:
        return render_template('relink.html', error=str(e))

# ======= Run =======

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
