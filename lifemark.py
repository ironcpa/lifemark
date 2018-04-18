# -*- coding: utf-8 -*-

import urllib
from flask import Flask, render_template, request, redirect, session
import db_handler
import imgur_handler
from data_define import LifemarkFieldDef, Lifemark
from pprint import pprint
from collections import OrderedDict
import json

application = Flask(__name__)
application.secret_key = 'dummy key'


def get_keywords_lines(lifemarks, keywords, search_fields=None):
    if not search_fields:
        search_fields = ()

    search_dict = OrderedDict()

    for e in lifemarks:
        lm = Lifemark(*e)
        lines = []
        for field in search_fields:
            field_data = lm[LifemarkFieldDef.index(field)]
            target_lines = field_data.split('\r\n')
            for line_no, line in enumerate(target_lines):
                for kw in keywords:
                    if kw.lower() in line:
                        d = (field, line_no, line)
                        if d not in lines:
                            lines.append(d)
        # if len(lines) == 0:
        #    continue
        search_dict[lm.key] = {'title': lm.title,
                               'lines': lines,
                               'category': lm.category,
                               'state': lm.state}

    # pprint(search_dict)
    return search_dict


@application.context_processor
def utility_processor():
    def get_lifemark_field(lifemark, fname):
        index = LifemarkFieldDef.index(fname)
        return lifemark[index]

    ''' try to create func for text results display
    def get_text_search_result_field(result, fname):
        return result[TextSearchResult.index(fname)]
        '''

    def get_imgur_thumbnail(src, type):
        if src is None or src == '':
            return ''
        ext_len = 4
        return src[:-ext_len] + type + src[-ext_len:]

    return dict(get_lifemark_field=get_lifemark_field,
                get_imgur_thumbnail=get_imgur_thumbnail)


def get_req_datetime(request):
    due_date = request.form.get('due_date')
    due_hour = request.form.get('due_hour')
    if not due_hour:
        due_hour = 0

    due_datetime = None if due_date == '' else \
        "{} {:02d}:00:00".format(due_date, int(due_hour))
    return due_datetime


@application.route('/')
def root():
    return 'this is flask root'


## doen't need this route: in nginx server config
#@application.route('/heart_beat')
#def heart_beat():
#    return 'it workds'


@application.route('/lifemarks', methods=['GET'])
def show_lifemarks():
    keywords = [k for k in request.values['keyword'].split()] \
               if 'keyword' in request.values else None
    is_all_match = request.values['is_all_match'] == 'on' \
                   if 'is_all_match' in request.values else False
    target_fields = [f for f in request.values['target_fields'].split()] \
                    if 'target_fields' in request.values else None
    target_states = [s for s in request.values['target_states'].split()] \
                    if 'target_states' in request.values else None
    in_ref = request.values['search_ref'] == 'on' \
             if 'search_ref' in request.values else False

    results = []
    text_results = None
    if keywords:
        print('keywords:', keywords)
        results = db_handler.get_lifemarks(keywords,
                                           is_all_match,
                                           target_fields,
                                           target_states,
                                           in_ref)

        text_results = get_keywords_lines(results,
                                          keywords,
                                          ('title', 'descr'))
    else:
        results = db_handler.get_all_lifemarks()
        text_results = get_keywords_lines(results,
                                          keywords)

    return render_template('lifemarks.html',
                           lifemarks=results,
                           categories=get_categories_w_empty(),
                           states=get_states(),
                           text_results=text_results)


@application.route('/search_lifemark', methods=['POST'])
def search_lifemark():
    return redirect('/lifemarks', code=307)


@application.route('/add_lifemark', methods=['POST'])
def add_lifemark():
    title = request.values['title']
    link = request.values['link']
    desc = request.values['desc']
    img_link = request.values['img_link']
    tags = request.values['tags']
    category = request.values['category'].lower()
    state = request.form.get('state')
    geo_lat = request.values['geo_lat'] if 'geo_lat' in request.values else 0
    geo_lon = request.values['geo_lon'] if 'geo_lon' in request.values else 0
    due_datetime = get_req_datetime(request)
    rating = request.form.get('rating')
    rating = None if rating == '' else rating

    rslt = db_handler.add_lifemark(title,
                                   link,
                                   desc,
                                   img_link,
                                   tags,
                                   category,
                                   geo_lat,
                                   geo_lon,
                                   state,
                                   due_datetime,
                                   rating)
    if rslt:
        return redirect('/lifemarks')
    else:
        return 'db error'


@application.route('/edit_lifemark', methods=['POST'])
def edit_lifemark():
    key = request.values['key']
    title = request.values['title']
    link = request.values['link']
    desc = request.values['desc']
    img_link = request.values['img_link']
    tags = request.values['tags']
    category = request.values['category'].lower()
    geo_lat = request.values['geo_lat'] if 'geo_lat' in request.values else 0
    geo_lon = request.values['geo_lon'] if 'geo_lon' in request.values else 0

    state = request.form.get('state')
    due_datetime = get_req_datetime(request)
    rating = request.form.get('rating')
    rating = None if rating == '' else rating

    rslt = db_handler.update_lifemark(key,
                                      title,
                                      link,
                                      desc,
                                      img_link,
                                      tags,
                                      category,
                                      geo_lat,
                                      geo_lon,
                                      state,
                                      due_datetime,
                                      rating)
    if rslt:
        return redirect('/lifemarks')
    else:
        return 'db error'


@application.route('/del_lifemark', methods=['POST'])
def del_lifemark():
    key = request.values['key']

    rslt = db_handler.del_lifemark(key)
    if rslt:
        return redirect('/lifemarks')
    else:
        return 'db error'


@application.route('/imgur_auth_callback')
def imgur_auth_callback():
    error = request.args.get('error', '')
    if error:
        return 'Error: ' + error

    # blow is not used yet =======================
    # state = request.args.get('state', '')

    access_token = imgur_handler.get_token(request.args.get('code'))

    if access_token:
        session['token'] = access_token

    params = {'token': access_token}
    url = '/show_all_images?' + urllib.parse.urlencode(params)
    return redirect(url)


@application.route('/show_all_images')
def show_all_images():
    token = request.args.get('token')
    if not token:
        if 'token' in session:
            token = session['token']

    if not token:
        print('redirect to imgur_auto_url')
        return redirect(imgur_handler.get_auth_url())

    rslt = imgur_handler.get_all_images(token)
    srslt = imgur_handler.get_latest_images(rslt, 5)

    return render_template('/images.html',
                           images=srslt,
                           categories=get_categories_w_empty(),
                           states=get_states())


@application.route('/imgur_login')
def imgur_login():
    return '<a href="{}">login</a>'.format(imgur_handler.get_auth_url())


@application.route('/show_map')
def show_map():
    lat = request.values['lat']
    lon = request.values['lon']
    return render_template('/show_map.html', geo_lat=lat, geo_lon=lon)


@application.route('/all_daily')
def all_daily():
    daily_list = db_handler.get_daily()

    dicts = [{'key': e[0], 'title': e[1], 'desc': e[2]}
                    for e in daily_list]

    rdict = {'results': dicts}
    js = json.dumps(rdict)
    print(js)
    return json.dumps(rdict)


@application.route('/save_daily', methods=['POST'])
def save_daily():
    req_data = request.values['save_json']
    dict = json.loads(req_data)
    pprint(dict)

    # save w/ db_handler
    #  - currently ignore title field from gridnote
    for e in dict['saves']:
        print(e)
        d = json.loads(e.replace('\r\n', '\\r\\n'))
        db_handler.update_lifemark_w_keywords(d['key'],
                                              descr=d['desc'])
    print('ok')

    return 'ok'


def get_categories_w_empty():
    categories = db_handler.get_categories()
    categories.insert(0, '')

    return categories


def get_states():
    return ['', 'todo', 'working', 'complete']


if __name__ == '__main__':
    application.run()

    # with app.test_request_context():
    #     print(url_for('hello'))
    #     print(url_for('profile', userno=555))
