import os
import requests
import urllib.parse
from dotenv import load_dotenv
from datetime import datetime, timedelta 
from flask import Flask, redirect, jsonify, request, session

app = Flask(__name__)
app.secret_key = os.urandom(24)

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = 'http://localhost:5000/callback'

auth_url = 'https://accounts.spotify.com/authorize'
token_url = 'https://accounts.spotify.com/api/token'
api_base_url = 'https://api.spotify.com/v1/'

@app.route('/')
def index():
    return "Welcome to my Spotify app <a href='/login'>Login with Spotify</a>"

@app.route('/login')
def login():
    scope = 'user-read-private user-read-email'
    
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': redirect_uri,
        'show_dialog': True  # Force user to login every time for debugging; remove for production
    }
    
    auth_url_full = f"{auth_url}?{urllib.parse.urlencode(params)}"
    
    return redirect(auth_url_full)

@app.route('/callback')
def callback():
    error = request.args.get('error')
    if error:
        return jsonify({"error": error})

    code = request.args.get('code')
    if not code:
        return jsonify({"error": "No authorization code received."})

    req_body = {
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret,
    }

    response = requests.post(token_url, data=req_body)
    token_info = response.json()

    if 'access_token' not in token_info:
        return jsonify({"error": "Access token not found in Spotify response."})

    session['access_token'] = token_info['access_token']
    session['refresh_token'] = token_info['refresh_token']
    session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']

    return redirect('/playlists')

@app.route('/playlists')
def get_playlists():
    if 'access_token' not in session or datetime.now().timestamp() > session.get('expires_at', 0):
        return redirect('/login')

    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    response = requests.get(api_base_url + 'me/playlists', headers=headers)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch playlists."})

    playlists = response.json()
    return jsonify(playlists)

@app.route('/getTracks')
def getTracks():
    return "some songs"


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)



