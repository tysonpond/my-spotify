import concurrent.futures
import config
import time
import pandas as pd
import requests
import numpy as np
from ast import literal_eval
import os

def worker_process(d):
	data = requests.get("https://api.spotify.com/v1/artists",
                   {"ids":",".join(d.tolist())},
                   headers=config.spotify_headers).json()["artists"]

	genres = [artist["genres"] if artist else [] for artist in data]

	time.sleep(1)

	return {artist:genre for artist,genre in zip(d,genres)}

def main():
	full_data = pd.read_csv(os.path.join(config.DATADIR, "with_IDs.csv"))
	data = full_data.loc[~full_data["artist_IDs"].isna()]
	data = data["artist_IDs"].apply(lambda x: literal_eval(x)).values
	data = np.unique(np.hstack(data))

	# split into arrays of size 50 because 50 is the maximum returned per API call
	data = [data[i:i + 50] for i in range(0, len(data), 50)] 

	res = {}
	with concurrent.futures.ProcessPoolExecutor() as executor:
		futures = [executor.submit(worker_process, d) for d in data]
		for future in concurrent.futures.as_completed(futures):
			this_res = future.result()
			if this_res:
				res.update(this_res)

	# rejoin with full data
	genres = []
	for artist_IDs in full_data["artist_IDs"].values:
		genres_this_row = []
		if isinstance(artist_IDs, str):
			artist_IDs = literal_eval(artist_IDs)
			for artist_ID in artist_IDs:
				genres_this_row.append(res[artist_ID])
		else:
			genres_this_row = "NA"

		genres.append(genres_this_row)

	full_data["genres"] = genres
	full_data.to_csv(os.path.join(config.DATADIR, "with_genres.csv"), index = False)

if __name__ == '__main__':
	main()