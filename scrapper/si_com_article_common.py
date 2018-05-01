import asyncio
from article_reader import get_bs_object, get_bs_object_async

SITE_URL = 'https://www.si.com'


async def get_article_detail(event_loop, index, article_url):
    bs = await get_bs_object_async(event_loop, article_url)

    title_tag = bs.find('h1')
    title = title_tag.text.strip() if title_tag else 'unknown'

    body_id = 'article-body'
    longbody_id = 'longform-body'

    content = bs.find('div', {'id': body_id})
    if not content:
        content = bs.find('div', {'id': longbody_id})
    if not content:
        return index, title, '!!! content not found\n' + url

    return index, title, content
