from inspect import Attribute
import requests
from bs4 import BeautifulSoup
import pandas as pd 

response = requests.get(
	url="https://en.wikipedia.org/wiki/List_of_high_schools_in_Indiana",
)

soup = BeautifulSoup(response.content, 'html.parser')
high_schools_api ="https://yearbook-app-33980.botics.co/api/highschools/"

tabols = soup.find_all("table",{"class":"wikitable"})
for tab in tabols:

    for row in tab.find_all('tr'):
        data = row.find_all(['td'])
        try:
            try:
                school = data[0].a.text
                data_obj = {'name':school }
                x = requests.post(high_schools_api, data = data_obj)

                print(x.status_code)
            except AttributeError:pass
        except IndexError:pass