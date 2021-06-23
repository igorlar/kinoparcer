import requests
import os
import cherrypy
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
import datetime

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
env = Environment(loader=FileSystemLoader(CUR_DIR))
URL = 'https://kinomax.ru/irkutsk'
URL1 = 'https://www.irk.ru/afisha/cinema/'

HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                         ' Chrome/90.0.4430.93 Safari/537.36', 'accept': '*/*'}


def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='d-flex border-bottom-1 border-stack film')
    films = []
    for item in items:
        time = []
        timeitem = item.find('div', class_='d-flex w-80').find_all('a')
        for item1 in timeitem:
            time.append(item1.get_text())
        time.sort()
        films.append({
            'title': item.find('a').get_text(),
            'img': item.find('img', class_='poster').get('srcset'),
            'zhanr': item.find('div', class_='d-flex fs-08 pt-3 text-main').find('div', class_='w-70').get_text(),
            'age': item.find('div', class_='fs-07 film-rating').get_text(),
            'time': time,
        })

    return films


def get_content1(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('li', class_='cinema-list__item j-film-row')
    films = []
    for item in items:
        cinema = []
        time1 = []
        cinemaitem = item.find_all('tr', class_='cinema-table__tr cinema-table__mobile-block')
        for item1 in cinemaitem:
            timeitem2d = item1.find_all('li', class_='time-list__item j-2d')
            timeitem3d = item1.find_all('li', class_='time-list__item j-3d')
            for a in timeitem2d:
                time1.append(a.find('time').get_text())
            for a in timeitem3d:
                time1.append(a.find('time').get_text())
            time1.sort()
            cinema.append({
                'cinema': item1.find('a').get_text(),
                'time': time1,
            })
            time1 = []
        for i in cinema:
            if (i['cinema'] == 'КиноМолл'):
                films.append({
                    'title': item.find('a', class_='cinema-list__title-link').get_text(strip=True),
                    'img': item.find('img', class_='cinema-list__img').get('src'),
                    'zhanr': item.find('span', class_='cinema-list__genre g-margin-right-10').get_text(),
                    'age': item.find('b').get_text(),
                    'time': i['time'],
                })

    return films


def parse(params):
    html = get_html(URL, params='date=' + params)
    if html.status_code == 200:
        return get_content(html.text)
    else:
        print('Error')


def parse1(params):
    html = get_html(URL1 + '/' + params)
    if html.status_code == 200:
        return get_content1(html.text)
    else:
        print('Error')


now = datetime.datetime.now()
class Parcer(object):
    @cherrypy.expose
    def index(self, calendar=None):
        if (calendar == None):
            calendar = now.strftime("%Y-%m-%d")
        films = parse(calendar)
        films1 = parse1(calendar[:4] + calendar[5:7] + calendar[8:10])
        c = 0
        films2 = []
        for item in films1:
            c = 0
            for item1 in films:
                if (item.get('title') == item1.get('title')):
                    c = c + 1
            if (c == 0):
                films2.append(item)
        template = env.get_template('text.html')
        return template.render(films=films, films1=films1, date=calendar,
                               max=(now + datetime.timedelta(days=7)).strftime("%Y-%m-%d"),
                               min=now.strftime("%Y-%m-%d"), films2=films2)


if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './'
        }
    }
    cherrypy.quickstart(Parcer(), '/', conf)
