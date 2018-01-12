from DBlogic import sqlal_queries as sq
import datetime

init_list = sq.read_from_file('conf')
DB = sq.DbSqlalQueries(init_list)


def test_update_category():
    trans = DB.connection.begin()
    try:
        assert DB.update_category(19, slug='slug_update') == \
               (19, 'new_cat_name', '//pass2//', '2description2', 'slug_update', 1)
    finally:
        trans.rollback()


def test_update_customer():
    trans = DB.connection.begin()
    try:
        assert DB.update_customer(3, password='password_update') == \
               (3,	'Denis', 'ralko@gmail.com', 'password_update', '0671773238', 'Kovalski 5')
    finally:
        trans.rollback()


def test_update_product():
    trans = DB.connection.begin()
    try:
        assert DB.update_product(5, other_info={'info': 'new'}) == \
               (5, 1, 'phone3', '//pass//',	'description', '//slug//3',	100, 25, {'info': 'new'})
    finally:
        trans.rollback()


def test_add_category():
    trans = DB.connection.begin()
    try:
        result = DB.add_category(cat_name='new_name', slug='new_slug', parent_id=1,
                               image_pass='//new//', description='new_desc')
        assert result[1:] == ('new_name', '//new//', 'new_desc', 'new_slug', 1)
    finally:
        trans.rollback()


def test_get_customer_by_login_and_password():
    assert DB.get_customer_by_login_and_password('Denis', 'qwerty') == \
           (3, 'Denis', 'ralko@gmail.com', 'qwerty', '0671773238', 'Kovalski 5')


def test_delete_customer():
    trans = DB.connection.begin()
    try:
        assert DB.delete_customer(3) == (3, 'Denis', 'ralko@gmail.com', 'qwerty', '0671773238', 'Kovalski 5')
    finally:
        trans.rollback()
