import json
import os
import requests
import sys
import time
from crawler import getData
from fuzzywuzzy import fuzz

# Downloads from the given url if the given file is null or out of date
def download_if_outdated(url, path, name, lifespan):
	lifespan *= 3600
	file_exists = os.path.exists(path)
	file_up_to_date = False
	if file_exists:
		file_up_to_date = os.path.getmtime(path) - time.time() < lifespan
	if not file_exists or not file_up_to_date:
		print("Updating " + name + "...", end = ' ')
		sys.stdout.flush()
		with open(path, "wb") as f:
			with requests.get(url, allow_redirects = True) as request:
				f.write(request.content)
		print("done.")
	else:
		print(name + " is up to date.")

# Returns the given subchild of the json object
def enumerate_json(data, enumeration):
	for i in range(0, len(enumeration)):
		data = data[enumeration[i]]
	return data

# Returns the given array from a json file
def array_from_json_file(path, array_location):
	array = {}
	with open(path, encoding='utf-8') as f:
		array = json.load(f)
	array = enumerate_json(array, array_location)
	return array

# Returns a list of tuples (int, data) with match strength
def fuzzy_query(query, data, str_location):
	results = []
	for i in range(0, len(data)):
		target = enumerate_json(data[i], str_location)
		if (len(target) > 1):
			strength = fuzz.partial_ratio(query.lower(), target.lower())
			results.append((strength, data[i]))
	return results

# Returns the top x results of the given list of tuples (int, data)
def top_x_results(results, x):
	results.sort(key = lambda tup: 100 - tup[0])
	top = []
	for i in range(0, min(x, len(results))):
		top.append(results[i][1])	
	return top

def main():
	# Update Steam games list
	download_if_outdated(
		"http://api.steampowered.com/ISteamApps/GetAppList/v0001/",
		"steam.json",
		"Steam games list",
		24
	)
	
	# Get games list
	games = array_from_json_file("steam.json", ["applist", "apps", "app"])
	
	# Get user input
	query = input("Search: ")
	
	# Get strength of query against game list
	query_results = fuzzy_query(query, games, ["name"])	
	
	# Find the top 10 matches
	top_results = top_x_results(query_results, 10)
	
	# Displays the top 10 matches
	for i in range(0, len(top_results)):
		print("\t" + str(i) + ") " + top_results[i]["name"])
		
	userSelect = input("Which game is correct: ")
	selectInt = int(userSelect)
	gameData = getData(top_results, selectInt)

		# Formats the array into a nice and clean JSON format
	print(json.dumps({"name": gameData[0],
					  "alt": gameData[1],
					  "date": gameData[2],
					  "dev": gameData[3],
					  "description": gameData[4],
					  "tags": gameData[5]}, sort_keys=True, indent=4, separators=(',', ': ')))

	# Finally allowing user to exit the program or search another game
	goAgain = input("Would you like to search another game (y/n): ")
	if (goAgain.lower() == "y"):
		main()
	
main()
