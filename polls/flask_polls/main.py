from polls.flask_polls import app
import json
from test.test_sqlal_queries import Manager


@app.route('/')
@app.route('/index')
def index():
    with Manager('conf') as DB:
        all_category = DB.get_all_categories()
        list_of_cat = list()
        for cat in all_category:
            list_of_cat.append(dict(cat))

    return json.dumps(list_of_cat)


if __name__ == "__main__":
    app.run()
