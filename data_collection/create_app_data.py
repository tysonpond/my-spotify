# After using the lastfm and spotify APIs to collect data, this script
# computes aggregate statistics which we use in our app.
# This code is derived from my jupyter notebook in 'data_analysis/Data analysis.ipynb'.

import pandas as pd
import os
import datetime
from dateutil.relativedelta import relativedelta
from ast import literal_eval
from sklearn.preprocessing import MinMaxScaler
from collections import Counter
import numpy as np
import json
from fuzzywuzzy import fuzz # fuzzy string matching

DATADIR = "../data"

# load data
df = pd.read_csv(os.path.join(DATADIR, "with_audio_features.csv"))
df = df.loc[~df["track_ID"].isna()] # if we couldnt find the track, we'll remove it

# convert timestamp (integer) to date
df["date"] = df["date"].apply(datetime.datetime.fromtimestamp) 

# handling genres
def get_genres_row(row):
    artist_IDs = row["artist_IDs"]
    if isinstance(artist_IDs, str):
        artist_IDs = literal_eval(artist_IDs)
        genres = literal_eval(row["genres"])
        
        # We'll just take the genres of the first artist (which we assume to be the 'main artist')
        # Alternatively we could concatenate all genres of all artists for the given track
        return genres[0]
    
    return np.nan
df["genres_proc"] = df[["artist_IDs","genres"]].apply(get_genres_row, axis = 1)

# defining and rescaling "qualitative" columns
qualitative = ['danceability', 'energy', 'loudness', 'speechiness','acousticness', 'instrumentalness', 'liveness', 'valence']
scaler = MinMaxScaler(feature_range=(0,100))
df[qualitative] = scaler.fit_transform(df[qualitative])

# let's get a view of the data with only unique tracks 
unique_tracks = df.loc[~df["track_ID"].duplicated()] 

# --- GET DAILY PLAYS ---
# today's date; we could also just use the last date in the data
today = datetime.date.today() 
# generate a time range from 1st day of previous month to last day of current month
idx = pd.date_range(today.replace(day=1) - relativedelta(months=1) , today + relativedelta(day=31))
# get the daily counts **for the days in the dataset** (if no songs played on a given day, this day will be missing)
daily_plays = df.set_index("date")["track_ID"].groupby(pd.Grouper(freq="D"))
# fill in missing days with 0
plays = pd.DataFrame(daily_plays.size().rename("plays").reindex(idx, fill_value = 0))

# --- DATA FOR HEATMAP ---
# get average value (grouped by day) for each qualitative feature 
qualities = df.set_index("date")[qualitative].groupby(pd.Grouper(freq="D")).mean()
# join with daily plays; left join ensures missing days will be kept 
df_out = plays.join(qualities, how = "left")
# write to file
df_out.to_csv(os.path.join(DATADIR, "heatmap.csv"), index_label = "date")

# --- DATA FOR RADAR ---
# get average value for each qualitative feature (across all dates), rename columns
df_out = unique_tracks[qualitative].mean().reset_index().rename(columns = {"index":"axis", 0:"value"})
# axis values are the qualities; sort in alphabetical order for cosmetic purposes 
df_out = df_out.sort_values("axis")
# convert to json
json_out = df_out.to_json(orient="records")
# write to file
with open(os.path.join(DATADIR, "radar.json"), "w") as f:
    f.write(json_out)

# --- DATA FOR TABLE ---
# --- top genres ---
# get top n tracks according to specified 'quality'
def get_top_tracks(unique_tracks, quality, n):
    if quality == "plays":
        keep_cols = ["track","artist","track_ID"]
    else:
        keep_cols = ["track","artist","track_ID"] + [quality]
        
    df_out = pd.merge(unique_tracks[keep_cols], 
         df.groupby("track_ID").size().rename("plays").reset_index(),
         on = "track_ID").drop("track_ID", axis=1).sort_values(quality, ascending = False)
    df_out = df_out.head(n)
    df_out["rank"] = np.arange(1,n+1)
    return df_out
data = {}
for col in ["plays"] + qualitative:
    data.update({col:json.loads(get_top_tracks(unique_tracks, quality=col, n=5).to_json(orient="records"))})
# write to file
with open(os.path.join(DATADIR, "table.json"), "w") as f:
    f.write(json.dumps(data))

# --- DATA FOR GENRES ---
# get top genres
common_genres = Counter(np.hstack(unique_tracks["genres_proc"].values)).most_common(50) 
genres_list = [x for x,count in common_genres]

# fuzzy matching to remove approximate duplicates (e.g. 'pop dance' ~= 'dance pop')
cutoff = 70 # if we find a pair of strings greater with a ratio greater than `cutoff` we will remove one of them
for g1 in genres_list:
    for g2 in genres_list:
        if g1 not in genres_list or g1 == g2:
            continue
        score = fuzz.token_sort_ratio(g1,g2) 
#         print((g1,g2),score)
        if score > cutoff:
            genres_list.remove(g2)

genres_list = genres_list[:10]

# --- top artists ---
top_artists = df.groupby("artist").size().sort_values(ascending=False).head(10)
artists_list = top_artists.index.values.tolist()

# --- combine ---
json_out = {"genres":genres_list, "artists":artists_list}
# write to file
with open(os.path.join(DATADIR,"genres.json"), "w") as f:
    f.write(json.dumps(json_out))

