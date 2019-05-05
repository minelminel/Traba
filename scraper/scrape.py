# Beautiful Soup parser function
import os
import json
import urllib3 as URL
from bs4 import BeautifulSoup


URL.disable_warnings(URL.exceptions.InsecureRequestWarning)


def Numbeo(city_name):
	url_root = 'https://www.numbeo.com/quality-of-life/in/'
	http = URL.PoolManager()
	r = http.request('GET', os.path.join(url_root,city_name.replace(' ','-').title()))
	if r.status == 200:
		soup = BeautifulSoup(r.data,'html.parser')
		try:
			table_data_numbers = soup.find_all("td",attrs={"style":"text-align: right"})
			table_data_labels = soup.find_all("a",attrs={"class":"discreet_link"})
			keys = []; values = []
			for tag in table_data_labels[1:]:
				keys.append(tag.text.strip().replace(' ','_'))
			for tag in table_data_numbers[1:]:
				values.append(float(tag.text.strip()))
			data_dict = dict(zip(keys,values))
			data_dict['Quality Sum'] = data_dict.pop('ƒ')
			return data_dict
		except:
			pass


def create_city_json(writeJSON=False):
	url_root = 'https://www.numbeo.com/cost-of-living/country_result.jsp?country=United+States'
	http = URL.PoolManager()
	r = http.request('GET', url_root)
	print('[STATUS: {}]'.format(r.status))
	soup = BeautifulSoup(r.data,'html.parser')
	table_data_labels = soup.find_all("a",attrs={"class":"discreet_link"})
	keys = []
	for tag in table_data_labels[2:]:
		keys.append(tag.text.strip())
	location_dict = {}
	for key in keys:
		city, state = key.split(',')
		location_dict[key] = {"City":city, "Abbreviation":state.strip(), "State":""}
	if writeJSON:
		with open('UScities.json', 'w') as fp:
			json.dump(location_dict, fp, sort_keys=True, indent=4)
	return location_dict


def create_tax_json(writeJSON=False):
	url_root = 'https://www.money-zine.com/financial-planning/tax-shelter/state-income-tax-rates/'
	http = URL.PoolManager()
	r = http.request('GET', url_root)
	# print('[STATUS: {}]'.format(r.status))
	soup = BeautifulSoup(r.data,'html.parser')
	table_data = soup.find_all("td")[2:]
	data_text = list(map(lambda items: items.get_text(), table_data))
	# labels = data_text[0:4]
	data_text = data_text[4:]
	State = []; Tax_Rate = []; Brackets = []; Top_Income_Range = []
	for i, data in enumerate(data_text):
		if data == '\xa0' or data == 'None':
			data = 'NO DATA'
		if (i)%4 == 0:
			State.append(data)
		elif (i)%4 == 1:
			Tax_Rate.append(data)
		elif (i)%4 == 2:
			Brackets.append(data)
		elif (i)%4 == 3:
			Top_Income_Range.append(data)
		else:
			pass
	tax_dict = {}
	for sta, tax, bra, top in zip(State, Tax_Rate, Brackets, Top_Income_Range):
		tax_dict[sta] = {"Tax_Rate":tax,"Brackets":bra,"Top_Income_Range":top}
	if writeJSON:
		with open('TaxData.json', 'w') as fp:
			json.dump(tax_dict, fp, sort_keys=True, indent=4)









# soup = BeautifulSoup(r.data,'html.parser')
# table_data_labels = soup.find_all("a",attrs={"class":"discreet_link"})
# keys = []
# for tag in table_data_labels[2:]:
# 	keys.append(tag.text.strip())
# location_dict = {}
# for key in keys:
# 	city, state = key.split(',')
# 	location_dict[key] = {"City":city, "Abbreviation":state.strip(), "State":""}
# if writeJSON:
# 	with open('UScities.json', 'w') as fp:
# 		json.dump(location_dict, fp, sort_keys=True, indent=4)
# print(location_dict)
