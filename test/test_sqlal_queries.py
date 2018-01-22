from DBlogic import sqlal_queries as sq
import sqlalchemy as sa


class Manager:
    def __init__(self, filename):
        self.filename = filename
        self.init_dict = sq.read_from_file(self.filename)
        self.name = self.init_dict['name']
        self.login = self.init_dict['login']
        self.password = self.init_dict['password']
        self.host = self.init_dict['host']

    def __enter__(self):
        self.DB = sq.DbSqlalQueries(self.name, self.login, self.password, self.host)
        self.trans = self.DB.connection.begin()
        return self.DB

    def __exit__(self, *args):
        self.trans.rollback()


def test_update_category():
    with Manager('conf') as DB:
        to_input = {'cat_name': 'TEST_name', 'image_pass': 'TEST_pass', 'description': 'TEST_desc',
                    'slug': 'TEST_slug', 'parent_id': 1}
        result_input = DB.add_category(**to_input)
        assert result_input[1:] == tuple(to_input.values())
        to_update = {'slug': 'new_slug'}
        result = DB.update_category(result_input['id'], **to_update)
        assert result['slug'] == to_update['slug']


def test_update_customer():
    with Manager('conf') as DB:
        to_input = {'user_name': 'TEST', 'email': 'TEST', 'password': 'TEST', 'phone': 'TEST',
                    'shipping_address': 'TEST'}
        result_input = DB.add_customer(**to_input)
        assert result_input[1:] == tuple(to_input.values())
        to_update = {'password': 'password_update'}
        result = DB.update_customer(result_input['id'], **to_update)
        assert result['password'] == to_update['password']


def test_update_product():
    with Manager('conf') as DB:
        to_input = {'category_id': 1, 'prod_name': 'TEST', 'image': 'TEST', 'description': 'TEST', 'slug': 'TEST',
                    'price_ua': 1, 'in_stock': 1, 'other_info': {'TEST': 'TEST'}}
        result_input = DB.add_product(**to_input)
        assert result_input[1:] == tuple(to_input.values())
        to_update = {'other_info': {'info': 'new'}}
        result = DB.update_product(result_input['id'], **to_update)
        assert result['other_info'] == to_update['other_info']


def test_get_customer_by_login_and_password():
    with Manager('conf') as DB:
        to_input = {'user_name': 'test_name', 'password': 'test_password', 'email': 'TEST',
                    'phone': 'TEST', 'shipping_address': 'TEST'}
        result_input = DB.add_customer(**to_input)
        assert DB.get_customer_by_login_and_password(to_input['user_name'], to_input['password']) == result_input


def test_delete_customer():
    with Manager('conf') as DB:
        to_input = {'user_name': 'test_name', 'password': 'test_password', 'email': 'TEST',
                    'phone': 'TEST', 'shipping_address': 'TEST'}
        result_input = DB.add_customer(**to_input)
        DB.delete_customer(result_input[0])
        select_text = sa.text("SELECT * FROM customer WHERE id = :id_customer ;")
        result = DB.connection.execute(select_text, id_customer=result_input[0]).fetchall()
        assert result == []
