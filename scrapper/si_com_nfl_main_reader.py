from urllib.request import urlopen
from bs4 import BeautifulSoup
from article_reader import get_bs_object, fetch_target
from si_com_article_common import SITE_URL, get_article_detail
import os


def get_article_urls(url):
    bs = get_bs_object(url)

    article_class = 'headline heading-content margin-8-bottom media-heading'
    articles = bs.findAll('h2', {'class': article_class})
    return [SITE_URL + e.a['href'] for e in articles if not e.a['href'].startswith('https')]


def main():
    fetch_target('https://www.si.com',
                 '/nfl',
                 'static/gen/si.com.nfl.html',
                 get_article_urls,
                 get_article_detail)


if __name__ == '__main__':
    os.chdir('..')
    main()
