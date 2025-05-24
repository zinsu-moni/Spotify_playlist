from flask import Flask, render_template, request, redirect, url_for, session
import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', str(uuid.uuid4()))

# Spotify configuration
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID', '7369e2ad40a641e096bb89169a408d17')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET', 'ae96de82982b41e4bdd2bc52f0075358')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:5000/callback')
SPOTIFY_SCOPE = 'playlist-modify-public'

@app.route('/')
def index():
    """Homepage with button to fetch Billboard Hot 100 and create playlist"""
    return render_template('index.html')

@app.route('/fetch-billboard')
def fetch_billboard():
    """Fetch Billboard Hot 100 chart data"""
    try:
        response = requests.get("https://www.billboard.com/charts/hot-100/")
        if response.status_code != 200:
            return render_template('error.html', message=f"Failed to fetch Billboard data: Status code {response.status_code}")
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Scrape songs and artists
        songs = []
        artists = []
        
        # Looking for the song titles
        song_elements = soup.select("li.o-chart-results-list__item h3#title-of-a-story")
        for song_element in song_elements:
            songs.append(song_element.get_text(strip=True))
        
        # Looking for the artist names
        artist_elements = soup.select("li.o-chart-results-list__item span.c-label.a-no-trucate")
        for artist_element in artist_elements:
            artists.append(artist_element.get_text(strip=True))
        
        # Make sure we have the same number of songs and artists
        min_length = min(len(songs), len(artists))
        songs = songs[:min_length]
        artists = artists[:min_length]
        
        songs_and_artists = list(zip(songs, artists))
        
        # Store in session
        session['songs_and_artists'] = songs_and_artists
        
        return render_template('songs.html', songs_and_artists=songs_and_artists)
    
    except Exception as e:
        return render_template('error.html', message=f"An error occurred: {str(e)}")

@app.route('/authorize')
def authorize():
    """Redirect to Spotify authorization page"""
    sp_oauth = SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SPOTIFY_SCOPE
    )
    
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    """Handle Spotify OAuth callback"""
    sp_oauth = SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SPOTIFY_SCOPE
    )
    
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    
    # Store token info in session
    session['token_info'] = token_info
    
    return redirect(url_for('create_playlist'))

@app.route('/create-playlist')
def create_playlist():
    """Create a Spotify playlist with Billboard Hot 100 songs"""
    token_info = session.get('token_info', None)
    songs_and_artists = session.get('songs_and_artists', [])
    
    if not token_info:
        return redirect(url_for('authorize'))
    
    if not songs_and_artists:
        return redirect(url_for('fetch_billboard'))
    
    # Set up Spotify client with OAuth token
    sp = spotipy.Spotify(auth=token_info['access_token'])
    
    # Get user ID
    user_id = sp.current_user()['id']
    
    # Search for tracks and get URIs
    uris = []
    track_details = []
    
    for song, artist in songs_and_artists:
        query = f"{song} {artist}"
        results = sp.search(q=query, type="track", limit=1)
        
        if results["tracks"]["items"]:
            track = results["tracks"]["items"][0]
            uris.append(track["uri"])
            track_details.append({
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'found': True
            })
        else:
            track_details.append({
                'name': song,
                'artist': artist,
                'found': False
            })
    
    # Create playlist if we found any tracks
    if uris:
        try:
            playlist = sp.user_playlist_create(
                user_id, 
                "Billboard Hot 100", 
                public=True,
                description="Billboard Hot 100 songs created with Spotify Playlist Generator"
            )
            
            # Add tracks to playlist in batches of 100 (Spotify API limit)
            for i in range(0, len(uris), 100):
                sp.playlist_add_items(playlist['id'], uris[i:i+100])
            
            playlist_url = playlist['external_urls']['spotify']
            return render_template('success.html', 
                                 playlist_url=playlist_url, 
                                 track_count=len(uris),
                                 track_details=track_details)
        
        except Exception as e:
            return render_template('error.html', message=f"Error creating playlist: {str(e)}")
    else:
        return render_template('error.html', message="No songs found on Spotify.")

if __name__ == '__main__':
    # Use PORT environment variable if it exists (for Render)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
