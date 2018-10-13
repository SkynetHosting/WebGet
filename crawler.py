import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

def getData(gameInfo, i):
	url = "https://store.steampowered.com/app/" + str(gameInfo[i]["appid"])
	
	# Getting and formatting the website
	http = urllib3.PoolManager()
	response = http.request('GET', url)
	soup = BeautifulSoup(response.data, "html.parser")
	
	# Formats the specific data points that we want
	results = []

	results.append(str(gameInfo[i]["appid"]))
	results.append(soup.find("div", attrs={"class": "apphub_AppName"}).text.strip())
	results.append(soup.find("div", attrs={"class": "date"}).text.strip())
	results.append(soup.find("div", attrs={"id": "developers_list"}).text.strip())
	results.append(soup.find("div", attrs={"class": "game_description_snippet"}).text.strip())
	tags = []
	tagNum = 0
	for foo in soup.find_all('div', attrs={"class": "glance_tags popular_tags"}):
		foo_descendants = foo.descendants
		for d in foo_descendants:
			if d.name == "a" and d.get("class", "") == ["app_tag"]:
				if tagNum < 4:
					tags.append(d.text.strip())
					tagNum = (tagNum + 1)
	results.append(tags)
	
	return results