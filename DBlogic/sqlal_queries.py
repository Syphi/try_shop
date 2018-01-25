import sqlalchemy as sa
import sqlalchemy.exc
import os
from slugify import slugify


def read_from_file(filename='conf'):
    result = {'host': 'localhost'}
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    filename = os.path.join(path, 'config', filename)
    with open(filename, 'r') as f:
        for line in f:
            data = line.split()
            result[data[0]] = data[2]
    return result


class DbSqlalQueries:

    def __init__(self, name, login, password, host):
        try:
            self.db_string = 'postgresql://' + login + ':' + password + '@' + host + '/' + name
            self.db = sa.create_engine(self.db_string)
            self.connection = self.db.connect()
            self.metadata = sa.MetaData()
            self.metadata.reflect(self.db)

            self.tables = self.init_tables()

            self.slug_number = 0

            print('Init class and connection')

        except (sa.exc.DBAPIError, sa.exc.DatabaseError) as e:
            print('no such db')
            print(e)

    def __del__(self):
        self.connection.close()

    @classmethod
    def parse(cls, string):
        name, login, password, host = map(str, string.split('-'))
        Db = cls(name, login, password, host)
        return Db

    def init_tables(self):
        tables = {}
        for key, value in self.metadata.tables.items():
            tables[key] = sa.Table(str(key), self.metadata, autoload=True, autoload_with=self.db)
        return tables

    def get_table(self, table_name):
        return self.tables[table_name]

    def generate_slug(self, table_name, txt):
        slug = slugify(txt, max_length=20)
        table = self.get_table(table_name)
        result = True
        num = 0
        while result is True:
            select = sa.select([table.c.slug]).where(table.c.slug == slug)
            select = sa.exists(select).select()
            result = self.connection.execute(select).fetchone()
            result = result[0]
            slug = f'{slug[:17]}-{num}'
            num += 1
        return slug

    def update_slug(self, table_name, new_name, id_name):
        table = self.get_table(table_name)
        select = sa.select([table.c.slug]).where(table.c.id == id_name)
        old_slug = self.connection.execute(select).fetchone()
        old_slug = old_slug[0]
        new_slug = slugify(new_name, max_length=20)
        if old_slug == new_slug:
            return old_slug
        else:
            return self.generate_slug(table_name, new_name)

    def add_category(self, cat_name, parent_id=None, image='', description=''):
        slug = self.generate_slug('category', cat_name)
        category_table = self.get_table('category')
        insert = sa.insert(category_table).returning(category_table)
        insert = insert.values({'cat_name': str(cat_name), 'image': str(image), 'description': str(description),
                                'slug': str(slug), 'parent_id': parent_id})
        return self.connection.execute(insert).fetchone()

    def add_product(self, category_id, prod_name, price_ua, in_stock, image='', description='', other_info='{}'):
        slug = self.generate_slug('product', prod_name)
        product_table = self.get_table('product')
        insert = sa.insert(product_table).returning(product_table)
        insert = insert.values({'category_id': category_id, 'prod_name': str(prod_name), 'image': str(image),
                               'description': str(description), 'slug': str(slug), 'price_ua': price_ua,
                               'in_stock': in_stock, 'other_info': other_info})
        return self.connection.execute(insert).fetchone()

    def add_customer(self, user_name, email, password, phone='', shipping_address=''):
        customer_table = self.get_table('customer')
        insert = sa.insert(customer_table).returning(customer_table)
        insert = insert.values({'user_name': str(user_name), 'email': str(email), 'password': str(password),
                                'phone': phone, 'shipping_address': shipping_address})
        return self.connection.execute(insert).fetchone()

    def add_orders(self, customer_id, sum_price, dictionary_with_products, delivery_data_time=None, payment_type=None):
        return_dictionary = {}

        order_table = self.get_table('orders')
        insert = sa.insert(order_table).returning(order_table)
        insert = insert.values({'customer_id': customer_id, 'sum_price': sum_price,
                                'delivery_data_time': delivery_data_time, 'payment_type': payment_type})
        return_dictionary['orders'] = self.connection.execute(insert).fetchone()

        order_product_table = self.get_table('order_products')
        insert = order_product_table.insert().returning(order_product_table)
        insert_list = []
        for key, value in dictionary_with_products.items():
            new_row = {'orders_id': return_dictionary['orders'][0], 'product_id': key, 'number_prod': value}
            insert_list.append(new_row)

        return_dictionary['order_products'] = self.connection.execute(insert, insert_list)
        return return_dictionary

    def get_all_categories(self):
        category_table = self.get_table('category')
        select = category_table.select()
        result = self.connection.execute(select).fetchall()
        return result

    def get_subcategories(self, category_id):
        category_table = self.get_table('category')
        select = category_table.select()
        select = select.where(category_table.c.parent_id == category_id)
        result = self.connection.execute(select).fetchall()
        return result

    def get_products_for_category(self, category_id):
        product_table = self.get_table('product')
        select = product_table.select()
        select = select.where(product_table.c.category_id == category_id)
        return self.connection.execute(select).fetchall()

    def get_order_info_by_order_id(self, order_id):
        orders_product_table = self.get_table('order_products')
        select = orders_product_table.select().\
            where(orders_product_table.c.orders_id == order_id)
        order_info = self.connection.execute(select).fetchall()
        return order_info

    def get_orders_for_customer(self, customer_id):
        orders_table = self.get_table('orders')
        select = orders_table.select().\
            where(orders_table.c.customer_id == customer_id)
        orders = self.connection.execute(select).fetchall()
        return orders

    def get_customer_by_login_and_password(self, login, password):
        customer_table = self.get_table('customer')
        select = customer_table.select().\
            where(customer_table.c.user_name == login).\
            where(customer_table.c.password == password)
        return self.connection.execute(select).fetchone()

    def update_category(self, category_id, **kwargs):
        if 'cat_name' in kwargs:
            kwargs['slug'] = self.update_slug('category', kwargs['cat_name'], category_id)
        category_table = self.get_table('category')
        update = category_table.update().returning(category_table)
        update = update.where(category_table.c.id == category_id).values(kwargs)
        return self.connection.execute(update).fetchone()

    def update_customer(self, customer_id, **kwargs):
        customer_table = self.get_table('customer')
        update = customer_table.update().returning(customer_table)
        update = update.where(customer_table.c.id == customer_id).values(kwargs)
        return self.connection.execute(update).fetchone()

    def update_product(self, product_id, **kwargs):
        if 'prod_name' in kwargs:
            kwargs['slug'] = self.update_slug('product', kwargs['prod_name'], product_id)
        product_table = self.get_table('product')
        update = product_table.update().returning(product_table)
        update = update.where(product_table.c.id == product_id).values(kwargs)
        return self.connection.execute(update).fetchone()

    def update_order(self, order_id, **kwargs):
        orders_table = self.get_table('orders')
        update = orders_table.update().returning(orders_table)
        update = update.where(orders_table.c.id == order_id).values(kwargs)
        return self.connection.execute(update).fetchone()

    def update_order_product(self, order_id, product_id, **kwargs):
        order_product_table = self.get_table('order_products')
        update = order_product_table.update().returning(order_product_table)
        update = update.where(sa.and_(order_product_table.c.orders_id == order_id,
                                      order_product_table.c.product_id == product_id)).\
            values({'orders_id': order_id, 'product_id': product_id, 'number_prod': kwargs['number_prod']})
        result = self.connection.execute(update)
        return result

    def delete_customer(self, id_customer):
        delete_str = sa.text('''DELETE FROM customer WHERE id = :id_customer;''')
        result_info = self.connection.execute(delete_str, id_customer=id_customer)
        return result_info

    def delete_order(self, id_order):
        delete_str = sa.text('''DELETE FROM orders WHERE id = :id_order;''')
        result = self.connection.execute(delete_str, id_order=id_order)
        return result