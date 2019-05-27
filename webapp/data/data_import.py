import os
import json
import requests
from pprint import pprint
from time import sleep

def get_state_names_from_json():
	jsonPath = os.path.join(os.path.dirname(__file__),'stateNames.json')
	jsonData = json.loads(open(jsonPath).read())
	States = []
	for data in jsonData:
		States.append(data["name"])
	return States


def get_state_abbreviations_from_json():
	jsonPath = os.path.join(os.path.dirname(__file__),'stateNames.json')
	jsonData = json.loads(open(jsonPath).read())
	States = []
	for data in jsonData:
		States.append(data["abbreviation"])
	return States


def get_state_abbreviation(state):
	jsonPath = os.path.join(os.path.dirname(__file__),'stateNames.json')
	jsonData = json.loads(open(jsonPath).read())
	if len(state) == 2:
		state = state.upper()
		for data in jsonData:
			if data['abbreviation'] == state:
				return state
			else:
				pass
	else:
		state = state.title()
		for data in jsonData:
			if data['name'] == state:
				return data['abbreviation']
			else:
				pass


def loadCitiesEnMasse(header_token,debug):
	# for item in list: api_request(_data)
	jsonPath = os.path.join(os.path.dirname(__file__),'UScities.json')
	jsonData = json.loads(open(jsonPath).read()) # <dict>
	# print(jsonData)
	# print(type(jsonData))
	successes = 0
	print('\t** LOADED DATA FROM FILE')
	for each in list(jsonData.values()):
		if debug:
			response = requests.get('http://localhost:5000/api/city',
									params=each,
									headers={'Token': header_token})
			pprint(each)
			print({'Token': header_token})
			print(response.json())
			print('\n\t** GET')
		else:
			response = requests.post('http://localhost:5000/api/city',
									params=each,
									headers={'Token': header_token})
			print('\n\t** POST')
		print(response.status_code)
		if response.status_code == 200:
			successes += 1
	return successes, len(jsonData)


def loadStatesEnMasse(header_token,debug):
	# for item in list: api_request(_data)
	jsonPath = os.path.join(os.path.dirname(__file__),'stateNames.json')
	jsonData = json.loads(open(jsonPath).read()) # <dict>
	# pprint(jsonData)
	# print(type(jsonData))
	successes = 0
	print('\t** LOADED DATA FROM FILE')
	for each in jsonData:
		if debug:
			response = requests.get('http://localhost:5000/api/state',
									params=each,
									headers={'Token': header_token})
			pprint(each)
			print({'Token': header_token})
			print(response.json())
			print('\n\t** GET')
		else:
			response = requests.post('http://localhost:5000/api/state',
									params=each,
									headers={'Token': header_token})
			print('\n\t** POST')
		print(response.status_code)
		if response.status_code == 200:
			successes += 1
	return successes, len(jsonData)



