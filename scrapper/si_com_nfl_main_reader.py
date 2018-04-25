from urllib.request import urlopen
from bs4 import BeautifulSoup
from article_reader import fetch_target, create_file, create_html_file
import si_com_article_common as sic


def fetch_articles(bs):
    article_class = 'headline heading-content margin-8-bottom media-heading'
    articles = bs.findAll('h2', {'class': article_class})
    return [a for a in articles if not a.a['href'].startswith('https')]


def main():
    fetch_target('https://www.si.com',
                 '/nfl',
                 'static/gen/si.com.nfl.html',
                 fetch_articles,
                 sic.get_article_detail_data,
                 sic.parse_article_detail)


if __name__ == '__main__':
    main()
