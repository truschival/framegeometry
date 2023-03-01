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
    geometrytable = soup.find('div', attrs={'id': 'geometrytable'})
    col_head = ['MfgDimNames', 'Desc']

    for row in geometrytable.findAll('tr', attrs={'class':'heading'}):
        for td in row.findAll('th', attrs={'name': 'framesize'}):
            col_head.append(td.text)
    df = pd.DataFrame(data=col_head).T

    for row in geometrytable.findAll('tr', attrs={'class':'property'}):
        prop = []
        for td in row.findAll('td'):
            if td.attrs['class'] == ['code']:
                prop.append(td.string)
            if td.attrs['class'] == ['name']:
                prop.append(td.contents[0] )   
            if td.attrs['class'] == ['value']:
                # Table data contains spans with either no class (text), 
                # ['value' 'value-mm'] ['value' 'value-inch'] or ['degrees']
                # read all except inches
                x = td.find(is_not_customary)
                prop.append(x.text)
            
        df = pd.concat([df, pd.DataFrame(prop).T])
    return df
    