import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

spotify_client_id = "7369e2ad40a641e096bb89169a408d17"
spotify_client_secret = "ae96de82982b41e4bdd2bc52f0075358"

response = requests.get("https://www.billboard.com/charts/hot-100/")
print(f"Billboard request status code: {response.status_code}")
soup = BeautifulSoup(response.text, "html.parser")

# Improved scraping to better find actual songs and artists
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
print(f"Found {len(songs)} songs and {len(artists)} artists")
print(f"First 3 songs and artists (if available): {songs_and_artists[:3] if songs_and_artists else 'None'}")

# Set up Spotify with Client Credentials for public data access
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=spotify_client_id,
    client_secret=spotify_client_secret
))
def get_spotify_uri(song, artist):
    query = f"{song} {artist}"
    results = sp.search(q=query, type="track", limit=1)
    if results["tracks"]["items"]:
        return results["tracks"]["items"][0]["uri"]
    else:
        return None
def get_spotify_uris(songs_and_artists):
    uris = []
    for song, artist in songs_and_artists:
        uri = get_spotify_uri(song, artist)
        if uri:
            uris.append(uri)
            print(f"Found Spotify URI for '{song}' by '{artist}'")
        else:
            print(f"❌ No Spotify URI found for '{song}' by '{artist}'")
    print(f"Total Spotify URIs found: {len(uris)} out of {len(songs_and_artists)}")
    return uris
def create_playlist(uris):
    print("\nTo create a playlist, you would need to authenticate with Spotify OAuth.")
    print("Here are the track URIs that would be added to your playlist:")
    for i, uri in enumerate(uris[:10], 1):
        track_info = sp.track(uri)
        print(f"{i}. {track_info['name']} by {track_info['artists'][0]['name']}")
    
    if len(uris) > 10:
        print(f"... and {len(uris) - 10} more tracks")
    
    print("\nTo actually create the playlist in your Spotify account, you would need to:")
    print("1. Set up OAuth authentication with 'playlist-modify-public' scope")
    print("2. Use a redirect URI that's registered in your Spotify Developer Dashboard")
    print("3. Handle the browser authentication flow")
    
def main():
    uris = get_spotify_uris(songs_and_artists)
    if uris:
        create_playlist(uris)
        print(f"\nTotal tracks found: {len(uris)}")
    else:
        print("No songs found on Spotify.")

if __name__ == "__main__":
    main()