from lxml import html
import requests
import re

extensions = ['mp4',
              'mpeg',
              'avi',
              'mkv',
              'wmv']

chanels = {
    'hogtied': 'Hogtied',
    'devicebondage': 'Device Bondage',
    'theupperfloor': 'The Upper Floor',
    'thetrainingofo': 'The Training of O',
    'kinkuniversity': 'Kink University',
    'sadisticrope': 'Sadistic Rope',
    'waterbondage': 'Water Bondage',
    'sexandsubmission': 'Sex and Submission',
    'fuckingmachines': 'Fucking Machines',
    'publicdisgrace': 'Public Disgrace',
    'hardcoregangbang': 'Hardcore Gangbang',
    'boundgangbangs': 'Bound Gangbang',
    'dungeonsex': 'Dungeon Sex',
    'animatedkink': 'Animated Kink',
    'whippedass': 'Whiped Ass',
    'divinebitches': 'Devine Bitches',
    'ultimatesurrender': 'Ultimate Surrender',
    'everythingbutt': 'Everything Butt',
    'electrosluts': 'Electro Sluts',
    'meninpain': 'Men in Pain',
    'wiredpussy': 'Wired Pussy',
    'footworship': 'Foot Worship',
    'tsseduction': 'TS Seduction',
    'tspussyhunters': 'TS Pussy Hunters',
    'third-party': 'External Production',
    'chantasbitches': 'Chantas Bitches',
    'captivemale': 'Captive male',
    'kinklive': 'Kink Live',
    'boundgods': 'Bound Gods',
    'menonedge': 'Men on Edge',
    'radrotica': ''

}


def search(term):
    print('https://www.kink.com/search?q=' + term)
    page = requests.get('https://www.kink.com/search?q=' + term)
    tree = html.fromstring(page.content)

    shoot = tree.xpath('/html/body/div[2]/div[1]/div[@class="shoot"]/div[2]/div[2]/div/a/text()')
    urls = tree.xpath('/html/body/div[2]/div[1]/div[@class="shoot"]/div[2]/div[2]/div/a/@href')
    dates = tree.xpath('/html/body/div[2]/div[1]/div[@class="shoot"]/div[2]/div[1]/div[1]/text()')
    images = tree.xpath('/html/body/div[2]/div[1]/div[@class="shoot"]/div[1]/a/img/@src')
    studios = tree.xpath('/html/body/div[2]/div[1]/div[@class="shoot"]/div[1]/a/span[1]/@class')
    studio_out = []
    for studio in studios:
        studio = studio.split()
        studio_out.append(chanels[studio[1]])

    print(studio_out)
    output = {
        'shoots': shoot,
        'urls': urls,
        'dates': dates,
        'images': images,
        'studios': studio_out
    }
    return output


def scrape_movie(target):
    # TODO:
    # Scrape rating
    # Scape Votes
    # Scrape trailer
    # Find runing time
    print('https://www.kink.com/shoot/' + target)
    page = requests.get('https://www.kink.com/shoot/' + target)
    tree = html.fromstring(page.content)

    name = tree.xpath('//h1[@class="shoot-title"]/text()')
    plot = tree.xpath('//div[@class="description"]/text()')
    plot = plot[3]
    date = tree.xpath('//div[@class="shoot-info"]/div[1]/div[1]/p[1]/text()')
    genres = {'BDSM'}
    studio = 'KINK'
    thumbs = tree.xpath('//*[@id="previewImages"]/div[@class="thumb"]/a/img/@src')
    # TODO:
    # Actors not parsed correctly
    actors_names = tree.xpath('/html/body/div[2]/div[1]/div[1]/div[4]/div[3]/div[1]/div[1]/p[2]/span/a/text()')
    actors_links = tree.xpath('/html/body/div[2]/div[1]/div[1]/div[4]/div[3]/div[1]/div[1]/p[2]/span/a/@href')

    channel = tree.xpath('//div[@class="column shoot-logo"]/a/@href')
    channel = channel[0].split('/')
    channel = channel[2]
    channel = chanels[channel]

    date = date[0].split(',')
    year = date[1].strip()
    date = date[0].split(' ')
    if len(date[2]) < 2:
        day = '0' + date[2]
    else:
        day = date[2]
    month = month_converter(date[1])

    output = {'name': name[0].strip(),
              'set': channel,
              'year': year,
              'plot': plot,
              'date': year + '-' + month + '-' + day,
              'genres': genres,
              'studio': studio,
              'thumbs': thumbs,
              'actors_names': actors_names,
              'actors_links': actors_links
              }
    print(output)
    return output


def detectId(string):
    match = re.search(r'\d{4}-\d{2}-\d{2}', string)
    if match:
        string = string.replace(match.group(), '')
    match = re.search(r'\d{2}-\d{2}-\d{2}', string)
    if match:
        string = string.replace(match.group(), '')
    match = re.search(r'\d{4}.\d{2}.\d{2}', string)
    if match:
        string = string.replace(match.group(), '')
    match = re.search(r'\d{2}.\d{2}.\d{2}', string)
    if match:
        string = string.replace(match.group(), '')
    detecetedIds = []
    string_parts = re.split('[\s . ( _]+', string)
    for string_part in string_parts:
        string_part = string_part.replace('(', '')
        string_part = string_part.replace(')', '')
        string_part = string_part.replace('[', '')
        string_part = string_part.replace(']', '')
        if string_part.isdigit():
            if detecetedIds.count(string_part) == 0:
                detecetedIds.append(string_part)
    return detecetedIds


def generateSearchString(string):
    match = re.search(r'\d{4}-\d{2}-\d{2}', string)
    if match:
        string = string.replace(match.group(), '')
    match = re.search(r'\d{2}-\d{2}-\d{2}', string)
    if match:
        string = string.replace(match.group(), '')
    match = re.search(r'\d{4}.\d{2}.\d{2}', string)
    if match:
        string = string.replace(match.group(), '')
    match = re.search(r'\d{2}.\d{2}.\d{2}', string)
    if match:
        string = string.replace(match.group(), '')
    detecetedIds = []

    # Let's do a basic split on _
    string_parts = re.split('[\s . ( _]+', string)
    for string_part in string_parts:
        string_part = string_part.replace('(', '')
        string_part = string_part.replace(')', '')
        string_part = string_part.replace('[', '')
        string_part = string_part.replace(']', '')
        if not string_part.isdigit() and extensions.count(string_part) == 0:
            if detecetedIds.count(string_part) == 0:
                detecetedIds.append(string_part)
    output = '+'.join(detecetedIds)
    return output

def get_poster(target):
    # TODO:
    # Poster still broken
    print(target)
    page = requests.get('https://www.kink.com/shoot/' + target)
    tree = html.fromstring(page.content)
    poster = tree.xpath('//div[@class="player"]/@poster')
    print(poster)
    return poster[0]

def month_converter(month):
    month = month.strip()[:3].lower()
    months = {'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04', 'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
              'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'}
    out = months[month]
    return out



