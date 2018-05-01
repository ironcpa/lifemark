from urllib.request import urlopen
from bs4 import BeautifulSoup
import asyncio
import requests
import os
from article_reader import fetch_target, print_articles, create_file
from article_reader import get_bs_object, get_bs_object_async

SITE_URL = 'https://www.clien.net'


def get_article_urls(url):
    article_class = 'section_list recommended'

    bs = get_bs_object(url)
    group = bs.findAll('div', {'class': article_class})
    articles = group[0].findAll('div', {'class': 'list_title'})

    return [SITE_URL + e.a['href'] for e in articles]


async def get_article_detail(event_loop, index, article_url):
    title_class = 'post_subject'

    bs = await get_bs_object_async(event_loop, article_url)

    title_tag = bs.find('h3', {'class': title_class})
    title = title_tag.span.text if title_tag else "can't parse title"
    content = bs.find('body').find('body')

    return index, title, content


def main():
    fetch_target('https://www.clien.net',
                 '',
                 'static/gen/clien.recommend.html',
                 get_article_urls,
                 get_article_detail)


if __name__ == '__main__':
    os.chdir('..')
    main()
