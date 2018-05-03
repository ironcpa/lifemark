import requests
from bs4 import BeautifulSoup

with requests.Session() as s:
    p = s.post('https://quora.com', data={
            'email': 'ironcpa@gmail.com',
            'password': '9513821uj!'
        })
    print(p.text)

    base_page = s.get('https://quora.com')
    bs = BeautifulSoup(base_page.content, 'html.parser')

    with open('quora_test.html', 'wt') as f:
        f.write(str(base_page.content))