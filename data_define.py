from collections import namedtuple
import collections


class FieldDef:
    def __init__(self, *fields):
        self.fields = fields
        self.fields_map = {k: v for v, k in enumerate(fields)}
        self.fields_str = ' '.join(fields)

    def namedtuple(self, name):
        return collections.namedtuple(name, self.fields_str)

    def index(self, key):
        return self.fields.index(key)


LifemarkFieldDef = FieldDef('key',
                            'cdate',
                            'udate',
                            'title',
                            'link',
                            'category',
                            'state',
                            'tags',
                            'descr',
                            'img_link',
                            'geo_lat',
                            'geo_lon',
                            'u_geo_lat',
                            'u_geo_lon',
                            'due_date',
                            'rating')
Lifemark = LifemarkFieldDef.namedtuple('Lifemark')

TextSearchResult = namedtuple('TextSearchResult',
                              'key field line_no text')


if __name__ == '__main__':
    lm = Lifemark('v_key',
                  'v_cdate',
                  'v_udate',
                  'v_title',
                  'v_link',
                  'v_category',
                  'v_state',
                  'v_tags',
                  'v_descr',
                  'v_img_link',
                  'v_geo_lat',
                  'v_geo_lon',
                  'v_u_geo_lat',
                  'v_u_geo_lon',
                  'v_due_date')
    print(lm)
