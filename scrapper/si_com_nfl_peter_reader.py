from urllib.request import urlopen
from bs4 import BeautifulSoup
import asyncio
from article_reader import fetch_target, create_file, create_html_file
import si_com_article_common as sic


def fetch_articles(bs):
    article_class = 'headline heading-content-small margin-8-bottom media-heading'
    articles = bs.findAll('h2', {'class': article_class})
    return articles


def main():
    fetch_target('https://www.si.com',
                 '/author/peter-king',
                 'static/gen/si.com.nfl.peter.html',
                 fetch_articles,
                 sic.get_article_detail_data,
                 sic.parse_article_detail)


if __name__ == '__main__':
    main()
