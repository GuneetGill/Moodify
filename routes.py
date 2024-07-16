from flask import Blueprint, redirect, url_for, session, render_template, request
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
import config
from utils import show_tracks, recent_tracks

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def landing():
    if 'token_info' in session:
        return redirect(url_for('main.recently_played'))
    else:
        return render_template('landing.html')

@main_bp.route('/authenticate')
def authenticate():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@main_bp.route('/callback')
def callback():
    sp_oauth = create_spotify_oauth()
    if 'code' not in request.args:
        return "Error: Missing authorization code", 400

    code = request.args['code']
    try:
        token_info = sp_oauth.get_access_token(code)
    except Exception as e:
        return f"Error 2: Failed to retrieve access token - {str(e)}", 400

    if token_info:
        session['token_info'] = token_info
        return redirect(url_for('main.recently_played'))
    else:
        return "Error: Failed to retrieve access token", 400

@main_bp.route('/get_playlists')
def get_playlists():
    token_info = session.get('token_info')
    if not token_info:
        return redirect(url_for('main.landing'))

    sp = create_spotify_client(token_info['access_token'])
    try:
        playlists = sp.current_user_playlists()
        playlists_html = ""
        for playlist in playlists['items']:
            playlist_name = playlist['name']
            playlist_id = playlist['id']
            playlists_html += f"<h2><a href='/analyze_playlist/{playlist_id}'>{playlist_name}</a><br><br>"
        return render_template('get_playlists.html', playlists_html=playlists_html)
    except Exception as e:
        return f"Error: {str(e)}"
    
@main_bp.route('/recently_played')
def recently_played():
    token_info = session.get('token_info')
    if not token_info:
        return redirect(url_for('main.landing'))

    sp = Spotify(auth=token_info['access_token'])
    
    try:
        final_mood, cover_art_urls, song_info = recent_tracks(sp)
        return render_template('recently_played.html', final_mood= final_mood, cover_art_urls=cover_art_urls, song_info=song_info) 
    except Exception as e:
        return f"{str(e)}"


@main_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.landing'))

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=config.client_id,
        client_secret=config.client_secret,
        redirect_uri=config.redirect_uri,
        scope=config.scope,
        cache_handler=FlaskSessionCacheHandler(session),
        show_dialog=True
    )

def create_spotify_client(access_token):
    return Spotify(auth=access_token)

    
@main_bp.route('/analyze_playlist/<playlist_id>')
def analyze_playlist(playlist_id):
    token_info = session.get('token_info')
    if not token_info:
        return redirect(url_for('main.landing'))

    sp = Spotify(auth=token_info['access_token'])
    
    try:
        final_mood, tracks_info, cover_art_urls  = show_tracks(sp, playlist_id)
        return render_template('analyze_playlist.html', final_mood= final_mood, tracks_info =tracks_info, cover_art_urls=cover_art_urls) 
    except Exception as e:
        print(e)
        return f"{str(e)}"
   



