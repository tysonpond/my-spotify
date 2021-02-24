import concurrent.futures
import config
import time
import pandas as pd
import requests
import os

def worker_process(d):
	search_results = requests.get("https://api.spotify.com/v1/search", 
					{"q": d[0] + " " + d[1], "type": "track", "limit":50},
					headers=config.spotify_headers).json()["tracks"]["items"]

	filtered_results = []
	for sr in search_results:
		# match on album first
		if sr["album"]["name"].lower() == d[2].lower():
			filtered_results.append(sr)

		# try matching on artist
		else:
			artists = [artist["name"].lower() for artist in sr["artists"]]
			if d[1].lower() in artists:
				filtered_results.append(sr)

	if filtered_results:
		best_match = max(filtered_results, key = lambda x: int(x["popularity"]))
		track_ID = best_match["id"]
		artist_IDs = [artist["id"] for artist in best_match["artists"]]
	else:
		track_ID, artist_IDs = "NA", "NA"

	time.sleep(2)

	return d.tolist() + [track_ID, artist_IDs]

def main():
	full_data = pd.read_csv(os.path.join(config.DATADIR, "last_month_tracks.csv"))

	collection_period = full_data["collection_period"].max()

	data = full_data.sort_values("date", ascending=False) # most recent songs are listed first
	
	# keeping the last ensures that duplicate tracks from earlier collection periods
	# are identified
	idx = ["track","artist","album"]
	data = data.loc[~full_data[idx].duplicated(keep="last")] 

	# now we can drop tracks that are outside our collection period
	data = data.loc[full_data["collection_period"] == collection_period]

	# drop these columns temporarily
	data = data.drop(["date","collection_period"], axis=1).values

	res = []
	with concurrent.futures.ProcessPoolExecutor() as executor:
		futures = [executor.submit(worker_process, d) for d in data]
		for future in concurrent.futures.as_completed(futures):
			res.append(future.result())

	# merge new IDs with track data
	res_df = pd.DataFrame(data = res, columns = idx + ["track_ID","artist_IDs"])
	combined_data = pd.merge(full_data, res_df, how = "left", on = idx)
	
	# merge old IDs
	# this servers 2 purposes
	# 1) tracks within this collection period which were collected previously
	# 2) tracks from all previous collection periods 
	if collection_period > 0: # then there is previous data
		missing = combined_data.loc[combined_data["track_ID"].isna()].drop(["track_ID","artist_IDs"], axis=1)
		previous_IDs = pd.read_csv(os.path.join(config.DATADIR, "with_IDs.csv"))
		previous_IDs = previous_IDs.loc[~previous_IDs[idx].duplicated(keep="last"), ["track","artist","album","track_ID","artist_IDs"]] 
		missing = pd.merge(missing, previous_IDs, how = "left")
		
		not_missing = combined_data.loc[~combined_data["track_ID"].isna()]
		combined_data = pd.concat([missing, not_missing]).sort_values("date", ascending=False)

	combined_data.to_csv(os.path.join(config.DATADIR, "with_IDs.csv"), index = False)

if __name__ == '__main__':
	main()