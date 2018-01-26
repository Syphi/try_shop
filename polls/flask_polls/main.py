import json
import decimal

from flask import Blueprint
from flask import request


from test.test_sqlal_queries import Manager


frontend = Blueprint('frontend', __name__)


def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError


@frontend.route('/')
@frontend.route('/all_category', methods=['GET'])
def get_all_category():

    with Manager('conf') as DB:
        all_category = DB.get_all_categories()
        list_of_cat = list()
        for cat in all_category:
            list_of_cat.append(dict(cat))

    return json.dumps(list_of_cat)


@frontend.route('/login', methods=['GET'])
def get_customer_by_login_and_password():

    login = request.args.get('username')
    password = request.args.get('password')

    with Manager('conf') as DB:
        user_full_info = dict(DB.get_customer_by_login_and_password(login, password))

    return json.dumps(dict(user_full_info))


@frontend.route('/list_of_purchases', methods=['GET'])
def get_orders_for_customer():
    customer_id = request.args.get('customer_id')
    result = []
    with Manager('conf') as DB:
        list_purchases = DB.get_orders_for_customer(customer_id)
        for list in list_purchases:
            result = dict(list)

    return json.dumps(result, default=decimal_default)


@frontend.route('/order_info', methods=['GET'])
def get_order_info_by_order_id():
    order_id = request.args.get('order_id')
    result = []

    with Manager('conf') as DB:
        order_info = DB.get_order_info_by_order_id(order_id)
        for list in order_info:
            result = dict(list)

    return json.dumps(dict(result))

@frontend.route('/product_for_category', methods=['GET'])
def get_products_for_category():
    category_id = request.args.get('category_id')
    result = []

    with Manager('conf') as DB:
        order_info = DB.get_products_for_category(category_id)
        for list in order_info:
            result = dict(list)

    return json.dumps(dict(result), default=decimal_default)


@frontend.route('/subcategories', methods=['GET'])
def get_subcategories():
    category_id = request.args.get('category_id')
    result = []

    with Manager('conf') as DB:
        order_info = DB.get_subcategories(category_id)
        for list in order_info:
            result = dict(list)

    return json.dumps(dict(result))
