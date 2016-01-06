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
        results = data
        for card in data:
            if card['name'].lower() == searchterm.lower():
                results = [card]
        if len(results) > limit:
            answer = u'_Showing only the first results\U00002026_'
            results = results[0:limit]
        else:
            answer = ''
        for card in results:
            if len(results) > 1:
                answer += '\n\n'
            answer += '*{name}*, '.format(name = card['name'])
            answer += '{types}'.format(types = ' '.join(card['types']).title())
            if 'subtypes' in card:
                answer += u' \U00002014 {subtypes}, '.format(subtypes = ' '.join(card['subtypes']).title())
            else:
                answer += ', '
            answer += encodeCost(card['cost'], True) +'\n'
            # answer += '*{cost}*\n'.format(cost = card['cost'].encode('utf-8'))
            if 'creature' in card['types']:
                answer += u'\U0001F5E1{power}/\U0001F6E1{toughness}\n'.format(power = str(card['power']).encode('utf-8'), 
                    toughness = str(card['toughness']).encode('utf-8'))
            if 'planeswalker' in card['types']:
                answer += u'\U0001F6E1{loyalty}\n'.format(loyalty = str(card['loyalty']).encode('utf-8'))
            oracleText = encodeCost(card['text'])
            oracleText = oracleText.replace('(', '_(')
            oracleText = oracleText.replace(')', ')_')
            answer += oracleText
        return answer
    else:
        return ""

def encodeCost(text, manaCost = False):

    hybrid = {
        'B/G': ':bg:',
        'B/R': ':br:',
        'G/U': ':gu:',
        'G/W': ':gw:',
        'R/G': ':rg:',
        'R/W': ':rw:',
        'U/B': ':ub:',
        'U/R': ':ur:',
        'W/U': ':wu:',
        '2/B': ':2b:',
        '2/U': ':2u:',
        '2/W': ':2w:',
        '2/G': ':2g:',
        '2/R': ':2r:',
        'U/P': ':pu:',
        'W/P': ':pw:',
        'R/P': ':pr:',
        'G/P': ':pg:',
        'B/P': ':pb:',
    }

    symbols = {
        'W': ':w:',
        'U': ':u:',
        'B': ':n:',
        'G': ':g:',
        'R': ':r:',
        'X': ':cx:',
        'Y': ':cy:',
        'Z': ':cz:',
        'T': ':t:',
        'S': ':s:'
    }

    for letter in hybrid:
        if manaCost:
            text = text.replace(letter, hybrid[letter])
        else:
            text = text.replace('{' + letter + '}', hybrid[letter])

    for letter in symbols:
        if manaCost:
            text = text.replace(letter, symbols[letter])
        else:
            text = text.replace('{' + letter + '}', symbols[letter])

    for colorless in range(15, 0, -1):
        if manaCost:
            replaced = re.sub('[^:]' + str(colorless) + '[^:]', ':{}:'.format(str(colorless)), text)
            if text != replaced:
                text = replaced
                break
        else:
            text = text.replace('{' + str(colorless) + '}', ':{}:'.format(str(colorless)))

    text = text.replace('{', '')
    text = text.replace('}', '')

    return text

def card(searchterm):
    data = jsonretrieve(searchterm)

    if data:
        for card in data:
            if card['name'].lower() == searchterm.lower():
                match = card
            else:
                match = data[0]
        return match['editions'][0]['image_url']
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
        

    
