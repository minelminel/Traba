import os
import json

def get_states_from_json():
	jsonPath = os.path.join(os.path.dirname(__file__),'stateNames.json')
	# print(jsonPath)
	jsonInput = json.loads(open(jsonPath).read())
	# print(jsonInput)
	States = []
	for data in jsonInput:
		States.append(data["name"])
		# print(data['name'])
	# print(States)
	return States