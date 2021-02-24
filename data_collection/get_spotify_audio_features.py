import concurrent.futures
import config
import time
import pandas as pd
import requests
import numpy as np
from pandas import json_normalize
import os

def worker_process(d):
	data = requests.get("https://api.spotify.com/v1/audio-features",
                   {"ids":",".join(d.tolist())},
                   headers=config.spotify_headers).json()["audio_features"]

	data = [x for x in data if x] # remove null results
	drop_keys = ["type", "uri", "track_href", "analysis_url"]
	data = [{key:dct[key] for key in dct if key not in drop_keys} for dct in data]

	time.sleep(1)

	return data

def main():
	full_data = pd.read_csv(os.path.join(config.DATADIR, "with_genres.csv"))
	data = full_data.loc[~full_data["track_ID"].isna(), "track_ID"]
	data = data.unique()

	# split into arrays of size 100 because 100 is the maximum returned per API call
	data = [data[i:i + 100] for i in range(0, len(data), 100)] 

	res = []
	with concurrent.futures.ProcessPoolExecutor() as executor:
		futures = [executor.submit(worker_process, d) for d in data]
		for future in concurrent.futures.as_completed(futures):
			this_res = future.result()
			if this_res:
				res.extend(this_res)

	res_df = json_normalize(res)
	out_df = pd.merge(full_data, res_df, how = "left", left_on = "track_ID", right_on = "id").drop("id",axis=1)
	out_df.to_csv(os.path.join(config.DATADIR, "with_audio_features.csv"), index = False)
	

if __name__ == '__main__':
	main()