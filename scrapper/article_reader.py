from urllib.request import urlopen
from bs4 import BeautifulSoup
import asyncio


def fetch_target(site_url,
                 section_url,
                 out_file_name,
                 article_list_func,
                 article_detail_func,
                 parse_article_detail_func):
    html = urlopen(site_url + section_url)
    bs = BeautifulSoup(html.read(), 'html.parser')

    articles = article_list_func(bs)
    detail_datas = article_detail_func(site_url, articles)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(fetch_article_detail(loop,
                                                 parse_article_detail_func,
                                                 detail_datas,
                                                 out_file_name))


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
    with open(file_name, 'wt') as f:
        for article in articles:
            f.write('[{}. {}]\n'.format(article[0], article[1]))
            f.write(article[2] + '\n\n')


def create_html_file(file_name, articles):
    print('debug:create_html_file:')
    print('\t', file_name)
    with open(file_name, 'wt') as f:
        f.write("<div style='max-width: 800px'>")
        for article in articles:
            if not article[2]:
                continue

            t = file_name.split('/')[-1].replace('.html', '')
            article_file = '{}_{}.html'.format(t, article[0])
            article_file_full = 'static/gen/' + article_file

            f.write("<a href='{}'>{}</a><br/>\n".format(article_file,
                                                        article[1]))
            with open(article_file_full, 'wt') as af:
                af.write("<div class='article' style='max-width: 800px'>")
                af.write("    <h1>{}. {}</h1>".format(article[0], article[1]))
                af.write("    <div>{}</div>".format(article[2]))
                af.write("</div>")
        f.write("</div>")
