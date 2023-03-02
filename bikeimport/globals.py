SCRAPE_HEADERS = {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.54',
          'DNT': '1',
          'Accept-Language': 'en,de;q=0.9',
          'Accept-Encoding': 'gzip, deflate',
          'Accept': '*/*',
          'Connection': 'keep-alive'
      }

def get_header():
    global SCRAPE_HEADERS
    return SCRAPE_HEADERS


def get_bike_categories():
    return ['endurance', 'race', 'gravel', 'cyclocross']

def normalize(word):
    return word.strip().lower().replace(' ', '-')