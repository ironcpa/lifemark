import os
import json
import requests
import urllib
from urllib.request import urlopen, Request

USER_NAME = 'ironcpa'
CLIENT_ID = os.environ['IMGUR_CLIENT_ID']
CLIENT_SECRET = os.environ['IMGUR_CLIENT_SECRET']
REDIRECT_URL = os.environ['IMGUR_REDIRECT_URL']


def get_auth_url():
    from uuid import uuid4
    state = str(uuid4())
    params = {'client_id': CLIENT_ID,
              'response_type': 'code',
              'state': state,
              'redirect_url': REDIRECT_URL}
    return 'https://api.imgur.com/oauth2/authorize?' + \
           urllib.parse.urlencode(params)


def get_token(auth_code):
    print('get_token:', auth_code)
    client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    post_data = {'grant_type': 'authorization_code',
                 'code': auth_code,
                 'redirect_url': REDIRECT_URL}
    response = requests.post('https://api.imgur.com/oauth2/token',
                             auth=client_auth,
                             data=post_data)
    token_json = response.json()
    return token_json['access_token']


def get_all_images(access_token):
    print('get_all_images:', access_token)
    headers = {'Authorization': 'Bearer {}'.format(access_token)}
    url_form = 'https://api.imgur.com/3/account/{}/images/{}'
    req = Request(url_form.format(USER_NAME, 0), headers=headers, method='GET')
    with urlopen(req) as res:
        data = json.loads(res.read().decode('utf-8'))
        return map(lambda i: (i['id'], i['link'], i['datetime']), data['data'])


def get_latest_images(all_images, count):
    s = sorted(all_images, key=lambda i: i[2], reverse=True)
    return s[:count]


def get_albums(client_id, username):
    headers = {'Authorization': 'Client-ID {}'.format(client_id)}
    url_form = 'https://api.imgur.com/3/account/{}/albums/{}'
    req = Request(url_form.format(username, 0), headers=headers, method='GET')

    with urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))

    return map(lambda item: '{}: {}: {}'.format(item['id'],
                                                item['title'],
                                                item['link']), data['data'])


# if __name__ == '__main__':
    # get_all_images()

    # links = get_albums('4a42b457c1afd48', 'ironcpa')
    # for l in links:
    #     print(l)
