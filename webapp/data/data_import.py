import os
import json


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
	state = state.title()
	for data in jsonData:
		if data['name'] == state:
			return data['abbreviation']
		else:
			pass

