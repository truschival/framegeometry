import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

def is_not_customary(tag):
    return not (tag.has_attr('class') and 'value-inch' in tag.attrs['class'])

def scrape(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.54',
        'DNT' : '1', 
        'Accept-Language': 'en,de;q=0.9', 
        'Accept-Encoding': 'gzip, deflate', 
        'Accept': '*/*', 
        'Connection': 'keep-alive'
    }

    r=requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'html5lib') 
    geometrytable = soup.find('table', attrs={'id': 'geometrie'})
    col_head = ['Desc', 'MfgDimNames']

    head = geometrytable.find('thead')
    row = head.find('tr')
    for td in row.findAll('th', attrs={'class': 'value'}):
        col_head.append(td.text.strip())
    
    col_head.append('Measuring Mode')
    df = pd.DataFrame(data=col_head).T

    body = geometrytable.find('tbody')
    for row in body.findAll('tr'):
        prop = []
        # description is a <th>
        desc = row.find('th')
        prop.append(desc.text.strip())

        for td in row.findAll('td'):
            prop.append(td.text.strip())
        df = pd.concat([df, pd.DataFrame(prop).T])
    print(df)
    return df

scrape("https://www.stevensbikes.de/2021/en/de/road/cyclocross/super-prestige-2x11/")