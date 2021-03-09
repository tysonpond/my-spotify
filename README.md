# My Spotify 🎵

## Overview
I built a pipeline to collect my daily Spotify activity using Python. To gain insights from my data, I made a web app using HTML/CSS/Javascript for the front-end and d3.js for 
making visualizations.

### Tags
Data collection, data pipeline, Spotify, interactive data visualizations, Python, Javascript (d3.js), web app

## Data collection
Spotify does not give access to your full listening history. Their API can only return your last 50 tracs. There is a "download your data" option on Spotify's "Privacy Settings" page, but it says it may take up to 30 days to complete. Our solution was to link a Last.fm account to Spotify, because they track (and store) Spotify streaming activity in real-time.

Our data collection pipeline is as follows:

0. `create_backup.py`
- Create a backup of all most recent data files.

1. `get_recent_tracks.py`
- Use Last.fm API to get my recent listening history on Spotify (track, artist, album, date).

2. `spotify_authentication.py`
- Use Selenium to automate Spotify Oauth process (optional). Otherwise, manually authenticate and update `config.py`.

3. `get_spotify_track_IDs.py`
- Use Spotify API to search the track + artist + album combination and get its track ID and the artist ID(s) of all featured artist(s). Merge with data from step 1.

4. `get_spotify_genres.py`
- Use Spotify API to get genres associated with each artist using the artist ID from step 3. Merge with data from step 3.

5. `get_spotify_audio_features.py`
- Use Spotify API to get audio features associated with each track ID from step 3. Merge with data from step 4.

6. `create_app_data.py`
- Compute aggregate statistics from merged data from step 5 such as number of daily plays. Generate data for several visualizations.

## TO DO
- Improve UI (grid layout)
- Improve tooltip UI on heatmap (better out-of-bounds checking)
- Idea: use a database (SQL) instead of working entirely with .csv. This isn't really needed for the small amount of data we're collecting, but it's good practice. Also may schedule our pipeline with cron or Airflow and host using AWS.
   - I've started implementing this
- Idea: show recent tracks/genres/artist (last 5, 10) in addition to "top"