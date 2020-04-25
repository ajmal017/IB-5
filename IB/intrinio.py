import requests
from bs4 import BeautifulSoup
r = requests.get('https://marketchameleon.com/Overview/GLOB/Earnings/Earnings-Dates')

soup = BeautifulSoup(r.text,'html.parser')

soup.findAll('ContentPlaceHolder1_rptearninghistory_lblEarningDate_0')
#soup.findAll(name = 'span',attrs={'id':'ContentPlaceHolder1_rptearninghistory_lblEarningDate_0'})[0].text
soup.findAll(name = 'tr',attrs={'data-excludegraph':'N'})[10].text.strip()
print('')



import numpy as np


