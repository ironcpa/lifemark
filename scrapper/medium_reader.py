from urllib.request import urlopen
from bs4 import BeautifulSoup
import asyncio
import requests
import os
from article_reader import fetch_target, print_articles, create_file, USER_AGENT
from article_reader import get_bs_object, get_bs_object_async


def get_article_urls(url):
    bs = get_bs_object(url)

    article_class = 'postArticle-readMore'
    group = bs.findAll('div', {'class': article_class})

    links = [div.a['href'] for div in group]
    return links


async def get_article_detail(event_loop, index, article_url):
    title_class = 'graf graf--h3 graf--leading graf--title'
    content_class = 'postArticle-content js-postField js-notesSource js-trackedPost'

    bs = await get_bs_object_async(event_loop, article_url)

    title_tag = bs.find('h1', {'class': title_class})
    title = title_tag.text if title_tag else ''

    content = ''

    style_links = bs.findAll('link', {'rel': 'stylesheet'})
    for e in style_links:
        content += str(e)

    content += str(bs.find('div', {'class': content_class}))

    return index, title, content


def main():
    target_urls = ['@cramforce/latest']
    for url in target_urls:
        base_url = 'https://medium.com'
        sub_url = '/' + url
        out_file = 'static/gen/medium.recent.html'
        fetch_target(base_url,
                     sub_url,
                     out_file,
                     get_article_urls,
                     get_article_detail)


if __name__ == '__main__':
    os.chdir('..')
    main()
