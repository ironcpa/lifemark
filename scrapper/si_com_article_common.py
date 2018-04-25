from urllib.request import urlopen
from bs4 import BeautifulSoup
import asyncio
from article_reader import create_html_file


def fetch_articles(bs):
    article_class = 'headline heading-content margin-8-bottom media-heading'
    articles = bs.findAll('h2', {'class': article_class})
    return articles


def get_article_detail_data(site_url, articles):
    detail_datas = {}
    for i, e in enumerate(articles):
        title = e.a.text
        detail_url = site_url + e.a['href']
        detail_datas[i] = (title, detail_url)
    return detail_datas


async def parse_article_detail(event_loop, index, title, url):
    print('debug:', url)
    html = await event_loop.run_in_executor(None, urlopen, url)
    bs = BeautifulSoup(html.read(), 'html.parser')

    body_id = 'article-body'
    longbody_id = 'longform-body'

    body = bs.find('div', {'id': body_id})
    if not body:
        body = bs.find('div', {'id': longbody_id})
    if not body:
        return index, title, '!!! content not found\n' + url

    '''
    paragraphs = body.findAll('p')
    content = ''
    for p in paragraphs:
        if p:
            content += p.text + '\n'
    '''
    content = body

    return index, title, content
