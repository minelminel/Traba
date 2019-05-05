import os
import json


def get_state_names_from_json():
	jsonPath = os.path.join(os.path.dirname(__file__),'stateNames.json')
	jsonInput = json.loads(open(jsonPath).read())
	States = []
	for data in jsonInput:
		States.append(data["name"])
	return States


def get_state_abbreviations_from_json():
	jsonPath = os.path.join(os.path.dirname(__file__),'stateNames.json')
	jsonInput = json.loads(open(jsonPath).read())
	States = []
	for data in jsonInput:
		States.append(data["abbreviation"])
	return States