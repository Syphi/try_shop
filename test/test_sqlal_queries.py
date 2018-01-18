from DBlogic import sqlal_queries as sq


class Manager:
    def __init__(self, filename):
        self.filename = filename
        self.init_list = sq.read_from_file(self.filename)
        self.name = self.init_list[0]
        self.login = self.init_list[1]
        self.password = self.init_list[2]
        self.host = self.init_list[3]

    def __enter__(self):
        self.DB = sq.DbSqlalQueries(self.name, self.login, self.password, self.host)
        self.trans = self.DB.connection.begin()
        return self.DB

    def __exit__(self, *args):
        self.trans.rollback()


def test_update_category():
    with Manager('conf') as DB:
        result_input = DB.add_category(cat_name='TEST', image_pass='TEST',
                                       description='TEST', slug='TEST', parent_id=1)
        to_update = {'slug': 'new_slug'}
        result = DB.update_category(result_input['id'], **to_update)
        assert result['slug'] == to_update['slug']


def test_update_customer():
    with Manager('conf') as DB:
        result_input = DB.add_customer(user_name='TEST', email='TEST', password='TEST',
                                       phone='TEST', shipping_address='TEST')
        to_update = {'password': 'password_update'}
        result = DB.update_customer(result_input['id'], **to_update)
        assert result['password'] == to_update['password']


def test_update_product():
    with Manager('conf') as DB:
        result_input = DB.add_product(category_id=1, prod_name='TEST', image='TEST', description='TEST', slug='TEST',
                                      price_ua=1, in_stock=1, other_info={'TEST': 'TEST'})
        to_update = {'other_info': {'info': 'new'}}
        result = DB.update_product(result_input['id'], **to_update)
        assert result['other_info'] == to_update['other_info']


def test_get_customer_by_login_and_password():
    with Manager('conf') as DB:
        assert DB.get_customer_by_login_and_password('Denis2', '2qwerty2') == \
               (4, 'Denis2', '2ralko2@gmail.com', '2qwerty2', '0671663238', 'Kovalski2')


def test_delete_customer():
    with Manager('conf') as DB:
        DB.delete_customer(4)
        result = DB.connection.execute("SELECT * FROM customer WHERE id = 4;").fetchall()
        assert result == []
