import os
import datetime
from urllib import parse
import psycopg2

LIFEMARK_TABLE = 'lifemark'
TEXT_FIELDS = ['title',
               'link',
               'descr',
               'tags',
               'img_link',
               'category',
               'state',
               'rating']


def as_kst(time_column):
    '''
    used when server timezone was utc
    server timezone changed on 20180401(kst)
    use as_simple_time(below) to format db timestamp columns
    '''
    return "to_char(({} at time zone 'UTC') at time zone 'KST', " \
           "'yyyyMMdd-HH24MISS')".format(time_column)


def as_simple_time(time_column):
    return "to_char({}, 'yyyyMMdd-HH24MISS')".format(time_column)


def get_conn():
    parse.uses_netloc.append('postgres')
    url = parse.urlparse(os.environ['DATABASE_URL'])

    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )

    return conn


def get_all_lifemarks():
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            sql = "select key, {}, {}, title, link, category, state, \n" \
                  "       tags, descr, img_link, geo_lat, geo_lon, \n" \
                  "       u_geo_lat, u_geo_lon, due_date, rating \n" \
                  "from {} \n" \
                  "order by udate desc \n" \
                  "limit %s".format(as_simple_time('cdate'),
                                    as_simple_time('udate'),
                                    LIFEMARK_TABLE)
            print(sql)
            cursor.execute(sql, (10,))
            rows = cursor.fetchall()
            return rows
    except Exception as e:
        print(e)
        return None


def get_lifemarks(keywords,
                  is_all_match=False,
                  target_fields=None,
                  target_states=None,
                  in_ref=False):
    default_target_fields = ['title',
                             'category',
                             'descr',
                             'tags',
                             'state']
    if not target_fields:
        target_fields = default_target_fields

    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            sql, params = make_all_match_condition_sql(target_fields,
                                                       keywords,
                                                       is_all_match,
                                                       target_states,
                                                       in_ref)
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return rows
    except Exception as e:
        print(e)
        return None


def get_daily_lifemarks():
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            search_fields = ['category']
            keywords = ['daily']
            sql, params = make_all_match_condition_sql(search_fields,
                                                       keywords)
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return rows
    except Exception as e:
        print(e)
        return None


def make_all_match_condition_sql(target_fields,
                                 keywords,
                                 is_all_match=False,
                                 target_states=None,
                                 in_ref=False):
    """
    not in_ref : search only in ref category
    """
    params = []
    where_concat = 'and' if is_all_match else 'or'

    where_clause = ''
    for i, keyword in enumerate(keywords):
        where_cond = '(' if i == 0 else ' {} ('.format(where_concat)
        for j, field in enumerate(target_fields):
            where_cond += '' if j == 0 else ' or '
            if field in TEXT_FIELDS:
                where_cond += 'lower({}) like lower(%s)'.format(field)
                params.append('%{}%'.format(keyword))
            else:
                where_cond += '{} = %s'.format(field)
                params.append('{}'.format(keyword))
        where_clause += where_cond + ')\n'

    if target_states:
        states = ', '.join(["'"+s+"'" for s in target_states])
        where_clause += "and state in ({}) \n".format(states)

    if in_ref:
        where_clause += "and category = 'ref' \n"

    sql = "select key, {}, {}, title, link, category, state, tags, \n" \
          "       descr, img_link, geo_lat, geo_lon, u_geo_lat, geo_lon, \n" \
          "       due_date, rating \n" \
          "from {} \n" \
          "where {} \n" \
          "order by udate desc".format(as_simple_time('cdate'),
                                       as_simple_time('udate'),
                                       LIFEMARK_TABLE,
                                       where_clause)
    print(sql)
    return sql, params


def get_categories():
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            sql = "select lower(category) " \
                  "from {} " \
                  "where category is not null and category != '' " \
                  "group by category".format(LIFEMARK_TABLE)
            cursor.execute(sql)
            rows = cursor.fetchall()
            return sorted([x[0] for x in rows])
    except Exception as e:
        print(e)
        return None


def add_lifemark(title,
                 link=None,
                 desc=None,
                 img_link=None,
                 tags=None,
                 category=None,
                 geo_lat=None,
                 geo_lon=None,
                 state=None,
                 due_date=None,
                 rating=None):
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            sql = "insert into {} (title, link, descr, img_link, tags, \n" \
                  "                category, geo_lat, geo_lon, \n" \
                  "                u_geo_lat, u_geo_lon, state, due_date, rating, \n" \
                  "                cdate, udate) \n" \
                  "values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, \n" \
                  "       '{}', \n" \
                  "       '{}')".format(LIFEMARK_TABLE,
                                      get_current_datetime(),
                                      get_current_datetime())
            cursor.execute(sql, (title,
                                 link,
                                 desc,
                                 img_link,
                                 tags,
                                 category,
                                 geo_lat,
                                 geo_lon,
                                 geo_lat,
                                 geo_lon,
                                 state,
                                 due_date,
                                 rating))
            conn.commit()

            return True
    except Exception as e:
        print(e)
        return False


def update_lifemark(key,
                    title=None,
                    link=None,
                    desc=None,
                    img_link=None,
                    tags=None,
                    category=None,
                    geo_lat=None,
                    geo_lon=None,
                    state=None,
                    due_date=None,
                    rating=None):
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            sql = "update {} " \
                  "set title = %s, " \
                  "    link = %s, " \
                  "    descr = %s, " \
                  "    img_link = %s, " \
                  "    tags = %s, " \
                  "    category = %s, " \
                  "    u_geo_lat = %s, " \
                  "    u_geo_lon = %s, " \
                  "    state = %s, " \
                  "    due_date = %s, " \
                  "    rating = %s, " \
                  "    udate = '{}' " \
                  "where key = %s".format(LIFEMARK_TABLE,
                                          get_current_datetime())
            cursor.execute(sql, (title,
                                 link,
                                 desc,
                                 img_link,
                                 tags,
                                 category,
                                 geo_lat,
                                 geo_lon,
                                 state,
                                 due_date,
                                 rating,
                                 key))
            conn.commit()

            return True
    except Exception as e:
        print(e)
        return False


def update_lifemark_w_keywords(key, **kwargs):
    '''
    update lifemark
     - optional fields is not changed if value is None
    '''
    if len(kwargs) == 0:
        return False

    set_clause = "set "
    params = []
    for k, v in kwargs.items():
        set_clause += "{} = %s \n".format(k)
        params.append(v)
    update_sql = ("update {} "
                  "{}"
                  "where key = {}").format(LIFEMARK_TABLE,
                                           set_clause,
                                           key)
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(update_sql, tuple(params))
            conn.commit()

            return True
    except Exception as e:
        print(e)
        return False


def del_lifemark(key):
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            sql = "delete from {} " \
                  "where key = %s".format(LIFEMARK_TABLE)
            cursor.execute(sql, (key,))
            conn.commit()

            return True
    except Exception as e:
        print(e)
        return False


def get_current_datetime():
    return str(datetime.datetime.now())


def get_dued_lifemarks():
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            # due_date - 2day : cuz due-date is next day's 00:00:00
            sql = "select key, title, category, state, due_date, descr \n" \
                  "from lifemark \n" \
                  "where state in ('todo') \n" \
                  "      and due_date - interval '2 day' < '{}'".format(get_current_datetime())
            #     "      and due_date - interval '2 day' < (current_timestamp - interval '9 hour')"
            print(sql)
            cursor.execute(sql)
            rows = cursor.fetchall()
            return rows
    except Exception as e:
        print(e)
        return None


def get_hourly_dued_lifemarks():
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            # due base: before 1 hour only
            sql = "select key, title, category, state, due_date, descr \n" \
                  "from lifemark \n" \
                  "where state in ('todo') \n" \
                  "      and extract(hour from due_date) != 0 \n" \
                  "      and due_date - interval '1 hour' < '{}'".format(get_current_datetime())
            print(sql)
            cursor.execute(sql)
            rows = cursor.fetchall()
            return rows
    except Exception as e:
        print(e)
        return None



def get_daily():
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            sql = "select key, title, descr \n" \
                  "from lifemark \n" \
                  "where category = 'daily' \n" \
                  "and state in ('todo', 'working') "
            cursor.execute(sql)
            rows = cursor.fetchall()
            return rows
    except Exception as e:
        print(e)
        return None


if __name__ == '__main__':
    results = get_all_lifemarks()
    print(results)
