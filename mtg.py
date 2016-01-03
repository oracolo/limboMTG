"""!card <card name> returns card image, !oracle <card name> returns card oracle text"""

try:
    from urllib import quote
except ImportError:
    from urllib.request import quote
import re
import requests
import json
from bs4 import BeautifulSoup

def jsonretrieve(searchterm):
    searchurl = "http://api.deckbrew.com/mtg/cards?name=" + searchterm
    result = requests.get(searchurl).text
    data = json.loads(result)
    return data

def oracle(searchterm):
    limit = 5
    data = jsonretrieve(searchterm)

    if data:
        if len(data) > 1:
            answer = u'_Showing only the first results\U00002026_'
        else:
            answer = ''
        for card in data[0:limit]:
            if len(data) > 1:
                answer += '\n\n'
            answer += '_{name}_, '.format(name = card['name'])
            answer += '{types}'.format(types = ' '.join(card['types']).title())
            if 'subtypes' in card:
                answer += u' \U00002014 {subtypes}, '.format(subtypes = ' '.join(card['subtypes']).title())
            else:
                answer += ', '
            answer += '*{cost}*\n'.format(cost = card['cost'].encode('utf-8'))
            if 'creature' in card['types']:
                answer += u'\U0001F5E1{power}/\U0001F6E1{toughness}\n'.format(power = str(card['power']).encode('utf-8'), 
                    toughness = str(card['toughness']).encode('utf-8'))
            if 'planeswalker' in card['types']:
                answer += u'\U0001F6E1{loyalty}\n'.format(loyalty = str(card['loyalty']).encode('utf-8'))
            answer += card['text']
        return answer
    else:
        return ""

def card(searchterm):
    data = jsonretrieve(searchterm)

    if data:
        card = data[0]
        return card['editions'][0]['image_url']
    else:
        return ""

def magiccardsParse(url):
	soup = BeautifulSoup(requests.get(url).text, "html5lib")
	name = soup.find('span', style="font-size: 1.5em;").find('a')
	image = soup.find('img', height="445")

	return image['src'] + "\n" + oracle(name.text)

def on_message(msg, server):
    text = msg.get("text", "")
    match = re.findall(r"!oracle (.*)", text)
    if match:
        searchterm = match[0]
        return oracle(searchterm.encode("utf8"))
    match = re.findall(r"!card (.*)", text)
    if match:
        searchterm = match[0]
        return card(searchterm.encode("utf8"))
    match = re.findall(r".*(http://magiccards.info/.*.html).*", text)
    if match:
        searchterm = match[0]
        return magiccardsParse(searchterm.encode("utf8"))
        

    
