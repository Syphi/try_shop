import json
import decimal

from flask import Blueprint
from flask import request
from flask import g

import DBlogic.new as db_logic

frontend = Blueprint('frontend', __name__)


def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError


@frontend.before_request
def before_request():
    init_dict = db_logic.read_from_file('conf')
    g.conn = db_logic.init_connection_to_db(init_dict['name'], init_dict['login'], init_dict['password'], init_dict['host'])
    g.DB = db_logic.DbSqlalQueries(g.conn)


@frontend.teardown_request
def teardown_request(exception):
    g.conn.close()


@frontend.route('/')
@frontend.route('/all_category', methods=['GET'])
def get_all_category():

    all_category = g.DB.get_all_categories()
    list_of_cat = list()
    for cat in all_category:
        list_of_cat.append(dict(cat))

    return json.dumps(list_of_cat)


@frontend.route('/login', methods=['GET'])
def get_customer_by_login_and_password():

    login = request.args.get('username')
    password = request.args.get('password')

    user_full_info = dict(g.DB.get_customer_by_login_and_password(login, password))

    return json.dumps(dict(user_full_info))


@frontend.route('/list_of_purchases', methods=['GET'])
def get_orders_for_customer():
    customer_id = request.args.get('customer_id')
    result = []
    list_purchases = g.DB.get_orders_for_customer(customer_id)
    for list in list_purchases:
        result = dict(list)

    return json.dumps(result, default=decimal_default)


@frontend.route('/order_info', methods=['GET'])
def get_order_info_by_order_id():
    order_id = request.args.get('order_id')
    result = []

    order_info = g.DB.get_order_info_by_order_id(order_id)
    for list in order_info:
        result = dict(list)

    return json.dumps(dict(result))

@frontend.route('/product_for_category', methods=['GET'])
def get_products_for_category():
    category_id = request.args.get('category_id')
    result = []

    order_info = g.DB.get_products_for_category(category_id)
    for list in order_info:
        result = dict(list)

    return json.dumps(dict(result), default=decimal_default)


@frontend.route('/subcategories', methods=['GET'])
def get_subcategories():
    category_id = request.args.get('category_id')
    result = []

    order_info = g.DB.get_subcategories(category_id)
    for list in order_info:
        result = dict(list)

    return json.dumps(dict(result))
