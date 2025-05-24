# Spotify Billboard Hot 100 Playlist Generator

This application automatically creates a Spotify playlist with the current Billboard Hot 100 songs.

## Requirements

Before you can use this application, you need to install the required packages:

```bash
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- Requests (HTTP library)
- BeautifulSoup4 (HTML parsing)
- Spotipy (Spotify API wrapper)
- Python-dotenv (environment variable management)

## Setting up Spotify Credentials

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
2. Create a new application
3. Set a Redirect URI to `http://localhost:5000/callback` for local testing
4. Copy your Client ID and Client Secret
5. Update the `.env` file with your credentials:
   ```
   SPOTIFY_CLIENT_ID=your-client-id
   SPOTIFY_CLIENT_SECRET=your-client-secret
   SPOTIFY_REDIRECT_URI=http://localhost:5000/callback
   SECRET_KEY=your-random-secret-key
   ```

## Running the Application Locally

1. Make sure you have Python installed (Python 3.7 or higher recommended)
2. Install the required packages: `pip install -r requirements.txt`
3. Run the application: `python app.py`
4. Open your browser and go to: `http://localhost:5000`

## Deploying to Vercel

1. Install Vercel CLI: `npm install -g vercel`
2. Login to Vercel: `vercel login`
3. Deploy the app: `vercel`
4. Set up environment variables in the Vercel dashboard:
   - `SPOTIFY_CLIENT_ID`
   - `SPOTIFY_CLIENT_SECRET`
   - `SPOTIFY_REDIRECT_URI` (your Vercel URL + `/callback`)
   - `SECRET_KEY`
5. Update the redirect URI in your Spotify Developer Dashboard to include your Vercel URL

## How It Works

1. The application scrapes the Billboard Hot 100 chart
2. It displays the list of found songs
3. After authorization with Spotify, it searches for each song
4. Creates a new playlist with the found songs
5. Provides a link to open the playlist in Spotify

## Files in this Project

- `app.py`: Main Flask application
- `requirements.txt`: Required Python packages
- `vercel.json`: Vercel deployment configuration
- `templates/`: HTML templates for the web interface
