import sqlalchemy as sa
import json


def read_from_file(filename):
    result = []
    filename = '/home/lenin/PycharmProjects/Shop/config/' + filename + '.txt'
    with open(filename, 'r') as f:
        for line in f:
            if 'name' in line:
                data = line.split()
                result.append(data[2])
            elif 'login' in line:
                data = line.split()
                result.append(data[2])
            elif 'password' in line:
                data = line.split()
                result.append(data[2])
    return result


class DbSqlalQueries:

    def __init__(self, conf_lst):
        try:
            self.db_string = 'postgresql://' + conf_lst[1] + ':' + conf_lst[2] + '@localhost/' + conf_lst[0]
            self.db = sa.create_engine(self.db_string)
            self.connection = self.db.connect()
            self.metadata = sa.MetaData()
            self.metadata.reflect(self.db)

            self.tables = {}
            for key, value in self.metadata.tables.items():
                self.tables[key] = sa.Table(str(key), self.metadata, autoload=True, autoload_with=self.db)

            print('Init class and connection')

        except Exception as e:
            print('shit - no such db')
            print(e)

    def __del__(self):
        self.connection.close()
        print('Close class and connection')

    def add_category(self, cat_name, slug, parent_id, image_pass='', description=''):
        insert = sa.insert(self.tables['category']).returning(self.tables['category'])
        insert = insert.values({'cat_name': str(cat_name), 'image': str(image_pass), 'description': str(description),
                                'slug': str(slug), 'parent_id': parent_id})
        return self.connection.execute(insert).fetchone()

    def add_product(self, category_id, prod_name, slug, price_ua, in_stock, image='', description='', other_info=json):
        insert = sa.insert(self.tables['product']).returning(self.tables['product'])
        insert = insert.values({'category_id': category_id, 'prod_name': str(prod_name), 'image': str(image),
                               'description': str(description), 'slug': str(slug), 'price_ua': price_ua,
                               'in_stock': in_stock, 'other_info': other_info})
        return self.connection.execute(insert).fetchone()

    def add_customer(self, user_name, email, password, phone='', shipping_address=''):
        insert = sa.insert(self.tables['customer']).returning(self.tables['product'])
        insert = insert.values({'user_name': str(user_name), 'email': str(email), 'password': str(password),
                                'phone': phone, 'shipping_address': shipping_address})
        return self.connection.execute(insert).fetchone()

    def add_orders(self, customer_id, sum_price, dictionary_with_products, delivery_data_time=None, payment_type=None):
        return_dictionary = {}
        '''add values to orders table'''
        insert = sa.insert(self.tables['orders']).returning(self.tables['orders'])
        insert = insert.values({'customer_id': customer_id, 'sum_price': sum_price,
                                'delivery_data_time': delivery_data_time, 'payment_type': payment_type})
        return_dictionary['orders'] = self.connection.execute(insert).fetchone()


        '''select last id in orders table by giving params'''
        select = self.tables['orders'].select()
        select = select.where(sa.and_(self.tables['orders'].c.customer_id == customer_id,
                                      self.tables['orders'].c.sum_price == sum_price,
                                      # self.orders.c.delivery_date_time == delivery_data_time, //how to
                                      self.tables['orders'].c.payment_type == payment_type))
        result_id = self.connection.execute(select).fetchall()
        result_id = result_id[-1][0]

        ''' parse dictionary_with_products and 
            add all values to orders_product name'''
        insert = self.tables['order_products'].insert().returning(self.tables['order_products'])
        insert_list = []
        for key, value in dictionary_with_products.items():
            new_row = {'orders_id': result_id, 'product_id': key, 'number_prod': value}
            insert_list.append(new_row)

        return_dictionary['order_products'] = self.connection.execute(insert, insert_list)
        return return_dictionary

    def get_all_categories(self):
        select = self.tables['category'].select()
        result = self.connection.execute(select).fetchall()
        return result

    def get_subcategories_by_id(self, category_id):
        select = self.tables['category'].select()
        select = select.where(self.tables['category'].c.parent_id == category_id)
        result = self.connection.execute(select).fetchall()
        print(result)

    def get_products_for_category(self, category_id):
        select = self.tables['product'].select()
        select = select.where(self.tables['product'].c.category_id == category_id)
        print(self.connection.execute(select).fetchall())
        return self.connection.execute(select).fetchall()

    def get_order_info_from_order_id(self, order_id):
        select = self.tables['order_products'].select().\
            where(self.tables['order_products'].c.orders_id == order_id)
        order_info = self.connection.execute(select).fetchall()
        return order_info

    def get_orders_for_customer(self, customer_id):
        select = self.tables['orders'].select().\
            where(self.tables['orders'].c.customer_id == customer_id)
        orders = self.connection.execute(select).fetchall()
        return orders

    def get_customer_by_login_and_password(self, login, password):
        select = self.tables['customer'].select().\
            where(self.tables['customer'].c.user_name == login).\
            where(self.tables['customer'].c.password == password)
        return self.connection.execute(select).fetchone()

    def update_category(self, category_id, **kwargs):
        update = self.tables['category'].update().returning(self.tables['category'])
        update = update.where(self.tables['category'].c.id == category_id).values(kwargs)
        return self.connection.execute(update).fetchone()

    def update_customer(self, customer_id, **kwargs):
        update = self.tables['customer'].update().returning(self.tables['customer'])
        update = update.where(self.tables['customer'].c.id == customer_id).values(kwargs)
        return self.connection.execute(update).fetchone()

    def update_product(self, product_id, **kwargs):
        update = self.tables['product'].update().returning(self.tables['product'])
        update = update.where(self.tables['product'].c.id == product_id).values(kwargs)
        return self.connection.execute(update).fetchone()

    def update_order(self, order_id, **kwargs):
        update = self.tables['orders'].update().returning(self.tables['orders'])
        update = update.where(self.tables['orders'].c.id == order_id).values(kwargs)
        return self.connection.execute(update).fetchone()

    def update_order_details(self, order_id, **kwargs):
        result_list = []
        for key, value in kwargs.items():
            update = self.tables['order_products'].update().returning(self.tables['order_products'])
            update = update.where(self.tables['order_products'].c.orders_id == order_id).\
                values({'orders_id': order_id, 'product_id': key, 'number_prod': value})
            result_list.append(self.connection.execute(update))
        return result_list

    def delete_customer(self, id_customer):
        result_lst = []
        delete_str = sa.text("SELECT id FROM orders WHERE customer_id = :id_customer")
        result = self.connection.execute(delete_str, id_customer=id_customer)

        if result.fetchone() != None:
            result_lst.append(result.fetchone())
            for res in result_lst:
                self.delete_order(res)

        delete_str = sa.text('''DELETE FROM customer WHERE id = :id_customer 
                             RETURNING customer.id, customer.user_name, customer.email, customer.password,
                             customer.phone, customer.shipping_address''')
        result_info = self.connection.execute(delete_str, id_customer=id_customer).fetchone()
        return result_info

    def delete_order(self, id_order):
        delete_str = sa.text('''DELETE FROM order_products WHERE orders_id = :id_order 
                                                RETURNING order_products.orders_id, order_products.product_id,
                                                 order_products.number_prod''')

        result = self.connection.execute(delete_str, id_order=id_order).fetchall()

        delete_str = sa.text('''DELETE FROM orders WHERE id = :id_order
                                         RETURNING orders.id, orders.customer_id, orders.sum_price,
                                         orders.payment_type, orders.delivery_data_time''')
        result += self.connection.execute(delete_str, id_order=id_order).fetchone()
        return result


conf = 'conf'
init_list = read_from_file(conf)

DB = DbSqlalQueries(init_list)
# result = DB.add_category(cat_name='name_cat--', image_pass='//pass2//',
#                    description='2description2', slug='slug2',  parent_id=1)
# DB.add_product(category_id=1, prod_name='phone2', image='//pass//', description='description', slug='//slug//2',
#                  price_ua=100, in_stock=25, other_info={})
# DB.add_customer(user_name='Denis2', email='2ralko2@gmail.com', password='2qwerty2',
#                   phone='0671663238', shipping_address='Kovalski2')
# DB.add_orders(customer_id=3, sum_price=777, delivery_data_time='2018-10-19 10:23:54+02',
#               payment_type='card', dictionary_with_products={1: 1, 5: 40})
# DB.get_category().sort(key=lambda x: x[0])
# DB.get_parent_category_by_id(4)
# DB.get_subcategories_by_id(1)
# DB.get_products_for_category(1)
# DB.get_orders_for_customer(1)
# DB.get_customer_by_login_and_password('Denis', 'qwerty')
# DB.delete_customer(1)
# DB.update_table_by_table_name('category', 19, cat_name='new_cat_name')
# result = DB.new_delete_order(63)
# DB.new_delete_customer(1)
# print(DB.new_get_orders_for_customer(3))
# print(DB.get_order_info_from_order_id(65))

