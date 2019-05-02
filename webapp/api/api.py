

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








class to_City_db(object):
	def __init__(self,*args):
		print("args: {}".format(*args))
		for arg in args: # seperate distinct input dicts
			print(arg)
			# parse dict headers
			print(arg['_head'])
			# determine handler from result
			func_list = ['_db','_msg','_xtra']
			




myDict = {"_head":"_db",
		"id":"1",
		"city":"buffalo",
		"state":"new york"}

cityObj = to_City_db(myDict,{"_head":"_msg","message":"hello world"})

