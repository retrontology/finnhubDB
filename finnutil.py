import requests
from bs4 import BeautifulSoup
import datetime
import finnhub
import time

def get_sp_500():
    members = []
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    r = requests.get(url)
    soup = BeautifulSoup(r.content) 
    table = soup.find('table', id='constituents')
    rows = table.findAll('tr')
    header = rows[0]
    rows = rows[1:]
    def clean_string(input:str): return input.replace('\n', '')
    for row in rows:
        columns = row.findAll('td')
        member = {
            'symbol': clean_string(columns[0].a.text),
            'security': clean_string(columns[1].a.text) if columns[1].a else clean_string(columns[1].text),
            'filings': columns[2].a.get('href'),
            'sector': clean_string(columns[3].text),
            'sub-industry': clean_string(columns[4].text),
            'headquarters': clean_string(columns[5].a.text),
            'first_added': datetime.datetime.strptime(clean_string(columns[6].text.split(' ')[0]), '%Y-%m-%d') if columns[6] and clean_string(columns[6].text) else None,
            'cik': clean_string(columns[7].text),
            'founded': clean_string(columns[8].text)
        }
        members.append(member)
    return members

def get_weighted_sp_500(finnhub_secret):
    client = finnhub.Client(api_key=finnhub_secret)
    members = get_sp_500()
    for member in members:
        failed = True
        while failed:
            try:
                profile = client.company_profile2(symbol=member['symbol'])
                failed = False
            except Exception as e:
                time.sleep(1)
        member['country'] = profile['country']
        member['currency'] = profile ['currency']
        member['exchange'] = profile ['exchange']
        member['market_cap'] = profile ['marketCapitalization']
        member['phone'] = profile ['phone']
        member['shares_outstanding'] = profile ['shareOutstanding']
        member['url'] = profile ['weburl']
        member['logo'] = profile ['logo']
    total_market_cap = sum([member['market_cap'] for member in members])
    for member in members:
        member['weighted_index'] = member['market_cap'] / total_market_cap
    members.sort(key = lambda x: x['weighted_index'], reverse=True)
    return members