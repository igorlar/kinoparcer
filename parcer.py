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
                img = item.find('img', class_='cinema-list__img')
                if (img == None):
                    img = "data:image/jpeg;base64,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"
                else:
                    img = img.get('src')
                films.append({
                    'title': item.find('a', class_='cinema-list__title-link').get_text(strip=True),
                    'img': img,
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
