from datetime import datetime
from dateutil.relativedelta import relativedelta
from time import mktime
import time
import requests
import pandas as pd
import config
import os


try:
    previous_data = pd.read_csv(os.path.join(config.DATADIR, "last_month_tracks.csv"))
except FileNotFoundError:
    # 1 month ago
    last_date = int(mktime((datetime.now() - relativedelta(months=1)).timetuple()))
    previous_data_flag, collection_period = False, 0
else:
    last_date = previous_data["date"].max()+1
    previous_data_flag, collection_period = True, previous_data["collection_period"].max()+1

now = int(mktime(datetime.now().timetuple()))

res = []
page = 1
totalPages = None
while not totalPages or page < totalPages:  
    data = requests.get("http://ws.audioscrobbler.com/2.0", 
                        {"method": "user.getrecenttracks", 
                         "user": "tysonpo", 
                         "limit": 200,
                         "page": page,
                         "from": last_date,
                         "to": now,
                         "api_key": config.lastfm_client_id, 
                         "format": "json"}).json()["recenttracks"]
    
    if page == 1:
        totalPages = int(data["@attr"]["totalPages"])

    # if a track is 'now playing' then it will not have a date. we'll avoid collecting this
    data = [track for track in data["track"] if "date" in track]
    
    res.extend([[track["name"], 
                 track["artist"]["#text"], 
                 track["album"]["#text"], 
                 track["date"]["uts"], 
                 collection_period] for track in data])
    
    page += 1
    time.sleep(2)

new_data = pd.DataFrame(data=res, columns=["track", "artist", "album", "date", "collection_period"])

if previous_data_flag:
    combined_data = pd.concat([new_data, previous_data])
    combined_data.to_csv(os.path.join(config.DATADIR, "last_month_tracks.csv"), index = False)
else:    
    new_data.to_csv(os.path.join(config.DATADIR, "last_month_tracks.csv"), index = False)