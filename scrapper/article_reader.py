from urllib.request import urlopen
from bs4 import BeautifulSoup
import asyncio
import requests

USER_AGENT = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Mobile Safari/537.36'


def get_bs_object(url):
    headers = {'User-Agent': USER_AGENT}
    res = requests.get(url, headers=headers)

    return BeautifulSoup(res.text, 'html.parser')

async def get_bs_object_async(event_loop, url):
    headers = {'User-Agent': USER_AGENT}
    res = await event_loop.run_in_executor(None, requests.get, url, headers)

    return BeautifulSoup(res.text, 'html.parser')

def fetch_target(site_url,
                 section_url,
                 out_file_name,
                 article_list_func,
                 article_detail_func):
    full_url = site_url + section_url
    article_urls = article_list_func(full_url)

    loop = asyncio.get_event_loop()

    futures = [asyncio.ensure_future(article_detail_func(loop, i, url)) for i, url in enumerate(article_urls)]
    results = loop.run_until_complete(asyncio.gather(*futures))

    print(results)
    create_html_file(out_file_name, results)


async def fetch_article_detail(event_loop,
                               parse_article_detail_func,
                               detail_datas,
                               out_file_name):
    futures = [asyncio.ensure_future(parse_article_detail_func(event_loop,
                                                               index,
                                                               val[0],
                                                               val[1]))
               for index, val in detail_datas.items()]
    result = await asyncio.gather(*futures)
    print('========== after gather ============')
    print(len(result))
    # print_articles(result)
    # create_file('si.com.nfl.txt', result)
    create_html_file(out_file_name, result)


def print_articles(articles):
    for article in articles:
        print(str(article[0]) + '.', article[1])
        print(article[2])
        print()


def create_file(file_name, articles):
    import os
    print(os.getcwd())
    with open(file_name, 'wt') as f:
        for article in articles:
            f.write('[{}. {}]\n'.format(article[0], article[1]))
            f.write(article[2] + '\n\n')


def create_html_file(file_name, articles):
    print('debug:create_html_file:')
    print('\t', file_name)
    print('\t', articles)
    no_cache = "<meta http-equiv='Cache-Control' content='no-store' />"
    viewport_meta = "<meta name='viewport' content='width=device-width, user-scalable=yes initial-scale=1'>"
    article_style = ''

    with open(file_name, 'wt') as f:
        f.write(no_cache)
        f.write(viewport_meta)
        f.write("<div style='max-width: 800px'>")
        for article in articles:
            print('debug:', article)
            if not article[2]:
                continue

            t = file_name.split('/')[-1].replace('.html', '')
            article_file = '{}_{}.html'.format(t, article[0])
            article_file_full = 'static/gen/' + article_file

            f.write("<h3><a href='{}'>{}</a><br/></h3>".format(article_file,
                                                        article[1]))
            with open(article_file_full, 'wt') as af:
                af.write(no_cache)
                af.write(viewport_meta)
                af.write("<meta http-equiv='Cache-Control' content='no-store' />")
                af.write("<div class='article' style='{}'>".format(article_style))
                af.write("    <h1>{}. {}</h1>".format(article[0], article[1]))
                af.write("    <div>{}</div>".format(article[2]))
                af.write("</div>")
        f.write("</div>")
