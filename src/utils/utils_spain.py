# -*- coding: utf-8 -*-
import re

SPAIN_LANGUAGES = ['es', 'ca', 'eu', 'gl']

def get_spain_places_regex():
    places = ['españa', 'catalunya', 'spain', 'madrid', 'espanya']
    places_regex_objs = []
    for place in places:
        regex_lugar = '.*{}.*'.format(place)
        places_regex_objs.append(re.compile(regex_lugar, re.IGNORECASE))
    return places_regex_objs