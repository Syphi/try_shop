from DBlogic import sqlal_queries as sq
import pytest
import sqlalchemy as sa


@pytest.fixture()
def DB():
    init_dict = sq.read_from_file('conf')
    DB = sq.DbSqlalQueries(init_dict['name'], init_dict['login'], init_dict['password'], init_dict['host'])
    trans = DB.connection.begin()
    yield DB
    trans.rollback()


def test_update_category(DB):

    to_input = {'cat_name': 'Test_slug', 'image': 'TEST_pass', 'description': 'TEST_desc',
                'parent_id': 1}
    result_input = dict(DB.add_category(**to_input))

    for key in to_input:
        assert result_input[key] == to_input[key]

    to_update = {'cat_name': 'new_slug'}
    result = DB.update_category(result_input['id'], **to_update)
    assert result['cat_name'] == to_update['cat_name']


def test_update_customer(DB):

    to_input = {'user_name': 'TEST', 'email': 'TEST', 'password': 'TEST', 'phone': 'TEST', 'shipping_address': 'TEST'}
    result_input = dict(DB.add_customer(**to_input))

    for key in to_input:
        assert result_input[key] == to_input[key]

    to_update = {'password': 'password_update'}
    result = DB.update_customer(result_input['id'], **to_update)
    assert result['password'] == to_update['password']


def test_update_product(DB):

    to_input = {'category_id': 1, 'prod_name': 'zxzxz', 'image': 'TEST', 'description': 'TEST',
                                  'price_ua': 1, 'in_stock': 1, 'other_info': {'TEST': 'TEST'}}
    result_input = dict(DB.add_product(**to_input))

    for key in to_input:
        assert result_input[key] == to_input[key]

    to_update = {'prod_name': 'new_Slug', 'other_info': {'info': 'new'}}
    result = DB.update_product(result_input['id'], **to_update)
    assert result['other_info'] == to_update['other_info']


def test_get_customer_by_login_and_password(DB):

    to_input = {'user_name': 'test_name', 'password': 'test_password', 'email': 'TEST',
                'phone': 'TEST', 'shipping_address': 'TEST'}
    result_input = DB.add_customer(**to_input)

    assert DB.get_customer_by_login_and_password(to_input['user_name'], to_input['password']) == result_input


def test_delete_customer(DB):

    to_input = {'user_name': 'test_name', 'password': 'test_password', 'email': 'TEST',
                'phone': 'TEST', 'shipping_address': 'TEST'}
    result_input = DB.add_customer(**to_input)

    DB.delete_customer(result_input[0])
    select_text = sa.text("SELECT * FROM customer WHERE id = :id_customer ;")

    result = DB.connection.execute(select_text, id_customer=result_input[0]).fetchall()
    assert result == []
