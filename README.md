# My Spotify tunes 🎵

## Overview
I built a pipeline to collect my daily Spotify activity using Python. To gain insights from my data, I made a web app using HTML/CSS/Javascript for the front-end and d3.js for 
making visualizations.

### Tags
Data collection, data pipeline, Spotify, interactive data visualizations, Python, Javascript (d3.js), web app

## Data collection
~~Spotify API does not give access to your listening history. There is a "download your data" option on Spotify's "Privacy Settings" page, but it says it may take up to 30 days to complete. Our solution was to link a Last.fm account to Spotify, because they track (and store) Spotify streaming activity in real-time.~~ See TODO section, I made this more complicated than needed 😞.

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

## TODO
- I realized Spotify API does in fact have a "Get Recent Tracks" option (which makes sense because how else would LastFM get access if Spotify doesn't make it available?). Silly me. It should be quick to replace steps 1 and 3 with just one API query.
- I should be able to schedule this process using Airflow.
- Make d3.js visualizations responsive
- Fix date range in `create_app_data.py` orelse data displayed may be incorrect on Mar 1.
- Improve tooltip on heatmap
- Idea: show recent tracks/genres/artist (last 5, 10) in addition to "top"