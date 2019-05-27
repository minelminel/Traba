import os
import re
import random
import requests
import urllib3 as URL
from time import time, sleep
from datetime import datetime
from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.options import Options

target = 'https://www.glassdoor.com/job-listing/devops-engineer-i-utilant-JV_IC1131850_KO0,17_KE18,25.htm?jl=3207060181&ctt=1558851031526'

http = URL.PoolManager()
r = http.request('GET', target)
html_doc = r.data.decode('utf-8')
soup = BeautifulSoup(html_doc, 'html.parser')
# print(soup.prettify())
print(soup.get_text())








"""
# # base url
# api_target_url = 'http://dummy.restapiexample.com/api/v1/employees'
api_target_url = 'https://www.glassdoor.com/job-listing/devops-engineer-i-utilant-JV_IC1131850_KO0,17_KE18,25.htm?jl=3207060181&ctt=1558851031526'

# Print HTML, Callback
def printPage(decodedpage,status):
    print('\n' + '_ ' * 42 + '\n')
    # print(rawbytes.decode('utf-8'))
    print(decodedpage)
    print('\n\n<Response [{}]>'.format(status))
    print('')
    print('_ ' * 42 + '\n')


# # Fetch page context
def fetchPage(target,display=True):
    http = URL.PoolManager()
    r = http.request('GET', target)
    try:
        page = r.data.decode('utf-8')
    except UnicodeDecodeError:
        page = r.data
    printPage(decodedpage=page,status=r.status)
    return page

fetchPage(api_target_url,display=True)


session = requests.Session()
payload = {'usr': 'admin', 'pwd': '12345'}
session.post(url=api_target_url, data=payload)
# subsequent requests that use the session will automatically handle cookies

r = session.get(api_target_url)
printPage(decodedpage=r.text,status=r.status_code)

# soup = BeautifulSoup(r.text, "html.parser")
# print(soup.find("div", {"class" : "success"}))
"""
"""
# Simple POST request
r = requests.post(api_target_url, data=dict(
    usr="admin",
    pwd="12345"
))
print(r.text)
print("\n<Response [{}]>".format(r.status_code))

soup = BeautifulSoup(r.text, "html.parser")
links = soup.find_all("form")
print(links)
"""
"""
links = soup.find_all("a")
tags = soup.find_all("li", "search-result")
tag = soup.find("div", id="bar")
tags = soup.find("div", id="search-results").find_all("a", "external-link
tags = soup.select("#search-results .external-links")
inner_contents = soup.find("div", id="price").contents
inner_text = soup.find("div", id="price").text.strip()
"""










"""
  >>> from bs4 import BeautifulSoup
  >>> soup = BeautifulSoup("<p>Some<b>bad<i>HTML")
  >>> print soup.prettify()
  <html>
   <body>
    <p>
     Some
     <b>
      bad
      <i>
       HTML
      </i>
     </b>
    </p>
   </body>
  </html>
  >>> soup.find(text="bad")
  u'bad'

  >>> soup.i
  <i>HTML</i>

  >>> soup = BeautifulSoup("<tag1>Some<tag2/>bad<tag3>XML", "xml")
  >>> print soup.prettify()
  <?xml version="1.0" encoding="utf-8">
  <tag1>
   Some
   <tag2 />
   bad
   <tag3>
    XML
   </tag3>
  </tag1>
"""

# # URL-based POST requet
# r = requests.get(api_target_url, params=dict(
#     query="web scraping",
#     page=2
# ))


















#
