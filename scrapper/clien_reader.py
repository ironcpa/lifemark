from urllib.request import urlopen
from bs4 import BeautifulSoup
import asyncio
from article_reader import fetch_target, print_articles, create_file


def get_articles(bs_object):
    article_class = 'section_list recommended'
    group = bs_object.findAll('div', {'class': article_class})
    articles = group[0].findAll('div', {'class': 'list_title'})

    return articles


def get_article_details(site_url, articles):
    detail_datas = {}
    for i, e in enumerate(articles):
        title_span = e.a.findAll('span', {'class': 'subject'})
        title = title_span[0].text

        detail_url = site_url + e.a['href']
        detail_datas[i] = (title, detail_url)

        print('debug: title:', title)
        print('debug: url:', detail_url)
    return detail_datas


async def get_article_detail(event_loop, index, title, url):
    html = await event_loop.run_in_executor(None, urlopen, url)
    bs = BeautifulSoup(html.read(), 'html.parser')

    title = bs.find('title').text
    paragraphs = bs.find('body').findAll('p')

    content = ''
    for p in paragraphs:
        if p and len(p.text.strip()) > 0:
            content += p.text + '\n'

    return index, title, content


async def fetch_detail(event_loop, detail_datas):
    futures = [asyncio.ensure_future(get_article_detail(event_loop,
                                                        index,
                                                        val[0],
                                                        val[1]))
               for index, val in detail_datas.items()]
    result = await asyncio.gather(*futures)
    print('========== after gather ============')
    print(len(result))
    # print_articles(result)
    create_file('clien_recommand.txt', result)


if __name__ == '__main__':
    fetch_target('https://www.clien.net',
                 '',
                 get_articles,
                 get_article_details,
                 fetch_detail)
