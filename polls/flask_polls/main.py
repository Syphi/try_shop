from flask import Flask
from flask import jsonify
from DBlogic import sqlal_queries as sq
from config import flack_config
from test.test_sqlal_queries import Manager


app = Flask(__name__)
app.debug = flack_config.DEBUG
app.host = flack_config.HOST
app.port = flack_config.PORT


@app.route('/')
@app.route('/index')
def index():
    with Manager('conf') as DB:
        all_category = DB.get_all_categories()
        list_of_cat = list()
        for v in all_category:
            cat = dict()
            for column, value in v.items():
                cat[column] = value
            list_of_cat.append(cat)

    return jsonify(list_of_cat)


if __name__ == "__main__":
    app.run()