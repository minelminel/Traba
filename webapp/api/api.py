# Traba
import os
import re
import json
import datetime
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    flash,
    session
)
from flask_api import (
    FlaskAPI,
    status,
    exceptions
)
api = FlaskAPI(__name__)

"""
# Function to convert number into string 
# Switcher is dictionary data type here 

def _msg(argdict):
	return argdict + ' message mod'

def _db(argdict):
	return argdict + ' database mod'

def _xtra(argdict):
	return argdict + ' extra mod'


def head_to_func(arg): 
    switcher = { 
        '_msg': _msg(arg), 
        '_db': _db(arg), 
        '_xtra': _xtra(arg), 
    } 
  
    # get() method of dictionary data type returns  
    # value of passed argument if it is present  
    # in dictionary otherwise second argument will 
    # be assigned as default value of passed argument 
    return switcher.get(argument, None) 
  

argument='_db'

res = head_to_func(argument)
print(res)

"""








class to_City_cls(object):
	def __init__(self,d):
		print("arg: {}\ntype: {}\n".format(d,type(d)))
		table_schema = {
			"header_keys":['_header','_token'],
			"db_keys":['id','city','state'],
			}
		subdict_header = {x: d[x] for x in table_schema['header_keys'] if x in d}
		print(subdict_header)

		
		subdict_db = {x: d[x] for x in table_schema['db_keys'] if x in d}
		print(subdict_db)
		"""
		# make sure all key-value pairs are present
		if set(table_schema['db_keys']) == set(list(subdict_db.keys())):
			print('keys in')
		else:
			print('keys not in')
		"""
		



myDict = {"_header":"_db",
		"_token":"correcthorsebatterystaple",
		"id":"1",
		"city":"buffalo",
		"state":"new york"}

cityObj = to_City_cls(myDict)

