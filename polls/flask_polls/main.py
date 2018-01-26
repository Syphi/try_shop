import json
from flask import Blueprint

from test.test_sqlal_queries import Manager


frontend = Blueprint('frontend', __name__)

@frontend.route('/')
@frontend.route('/index')
def index():
    with Manager('conf') as DB:
        all_category = DB.get_all_categories()
        list_of_cat = list()
        for cat in all_category:
            list_of_cat.append(dict(cat))

    return json.dumps(list_of_cat)
