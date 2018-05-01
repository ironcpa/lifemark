import asyncio
from article_reader import fetch_target, get_bs_object
from si_com_article_common import SITE_URL, get_article_detail
import os


def get_article_urls(url):
    bs = get_bs_object(url)

    article_class = 'headline heading-content-small margin-8-bottom media-heading'
    articles = bs.findAll('h2', {'class': article_class})
    return [SITE_URL + e.a['href'] for e in articles if not e.a['href'].startswith('https')]


def main():
    fetch_target('https://www.si.com',
                 '/author/peter-king',
                 'static/gen/si.com.nfl.peter.html',
                 get_article_urls,
                 get_article_detail)


if __name__ == '__main__':
    os.chdir('..')
    main()
