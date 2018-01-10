import sqlalchemy as sa
import json

def read_from_file(filename):
    result = []
    filename += '.txt'
    with open(filename, 'r') as f:
        for line in f:
            if 'name' in line:
                data = line.split()
                result.append(data[2])
            if 'login' in line:
                data = line.split()
                result.append(data[2])
            if 'password' in line:
                data = line.split()
                result.append(data[2])
    return result


class DbSqlalQueries:

    def __init__(self, name, login, password):
        try:
            self.db_string = 'postgresql://' + login + ':' + password + '@localhost/' + name
            self.db = sa.create_engine(self.db_string)
            self.connection = self.db.connect()
            self.metadata = sa.MetaData()
            self.metadata.reflect(self.db)

            self.tables = {}
            for key, value in self.metadata.tables.items():
                self.tables[key] = sa.Table(str(key), self.metadata, autoload=True, autoload_with=self.db)

            # self.orders = self.metadata.tables['orders']
            # self.customer = self.metadata.tables['customer']
            # self.product = self.metadata.tables['product']
            # self.category = self.metadata.tables['category']
            # self.order_products = self.metadata.tables['order_products']
            # self.orders = sa.Table('orders', self.metadata, autoload=True, autoload_with=self.db)
            # self.customer = sa.Table('customer', self.metadata, autoload=True, autoload_with=self.db)
            # self.product = sa.Table('product', self.metadata, autoload=True, autoload_with=self.db)
            # self.category = sa.Table('category', self.metadata, autoload=True, autoload_with=self.db)
            # self.order_products = sa.Table('order_products', self.metadata, autoload=True, autoload_with=self.db)
            print('Init class and connection')
        except Exception as e:
            print('shit - no such db')
            print(e)

    def __del__(self):
        self.connection.close()
        print('Close class and connection')

    def add_category(self, cat_name, slug, parent_id, image_pass = '', description = ''):
        insert = sa.insert(self.tables['category']).returning(self.tables['category'])
        insert = insert.values({'cat_name': str(cat_name), 'image': str(image_pass), 'description': str(description),
                                'slug': str(slug), 'parent_id': parent_id})
        for cat_name in self.connection.execute(insert):
            print(cat_name)

    def add_product(self, category_id, prod_name, slug, price_ua, in_stock, image='', description='', other_info=json):
        insert = sa.insert(self.tables['product']).returning(self.tables['product'])
        insert = insert.values({'category_id': category_id, 'prod_name': str(prod_name), 'image': str(image),
                               'description': str(description), 'slug': str(slug), 'price_ua': price_ua,
                               'in_stock': in_stock, 'other_info': other_info})
        for category_id in self.connection.execute(insert):
            print(category_id)

    def add_customer(self, user_name, email, password, phone ='', shipping_address=''):
        insert = sa.insert(self.tables['customer']).returning(self.tables['product'])
        insert = insert.values({'user_name': str(user_name), 'email': str(email), 'password': str(password),
                                'phone': phone, 'shipping_address': shipping_address})
        for user_name in self.connection.execute(insert):
            print(user_name)

    def add_orders(self, customer_id, sum_price, dictionary_with_products, delivery_data_time=None, payment_type=None):

        '''add values to orders table'''
        insert = sa.insert(self.tables['orders']).returning(self.tables['orders'])
        insert = insert.values({'customer_id': customer_id, 'sum_price': sum_price,
                                'delivery_data_time': delivery_data_time, 'payment_type': payment_type})
        for customer_id in self.connection.execute(insert):
            print(customer_id)

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

        for some in self.connection.execute(insert, insert_list):
            print(some)

    def get_all_categories(self):
        select = self.tables['category'].select()
        result = self.connection.execute(select).fetchall()
        return result

    def get_subcategories_by_id(self, category_id):
        select = self.tables['category'].select()
        select = select.where(self.tables['category'].c.parent_id == category_id)
        result = self.connection.execute(select).fetchall()
        print(result)

    def get_parent_category_by_id(self, category_id):
        select = self.tables['category'].select()
        select = select.where(self.tables['category'].c.id == category_id)
        result = self.connection.execute(select).fetchone()

        print(result)
        result_lst = []
        result_lst.append(result)
        while result[-1] != None:
            select = self.tables['category'].select()
            select = select.where(self.tables['category'].c.id == result[-1])
            result = self.connection.execute(select).fetchone()
            result_lst.append(result)
        print(result_lst)
        return result_lst

    def get_products_for_category(self, category_id):
        select = self.tables['product'].select()
        select = select.where(self.tables['product'].c.category_id == category_id)
        print(self.connection.execute(select).fetchall())
        return self.connection.execute(select).fetchall()

    def get_orders_for_customer(self, customer_id):
        '''
        need to give customer and order info
        use 3 tables customer, orders, order_products

        join with orders.id == orders_products.orders_id
        :return: dict{{'Client_info': (id, user_name, email, password, phone, addres),
        'Order_info': [(order.id, order.customer_id, order.sum_price, order.datetime, order.payment_type) ]}

        '''
        select = self.tables['customer'].select().\
            where(self.tables['customer'].c.id == customer_id)
        client_info = self.connection.execute(select).fetchall()[0]

        result_dict = {'Client_info': client_info}

        join = self.tables['orders'].join(self.tables['order_products'],
                                self.tables['orders'].c.id == self.tables['order_products'].c.orders_id)
        result = sa.select([self.tables['orders'], self.tables['order_products']]).select_from(join)
        orders_lst = self.connection.execute(result).fetchall()

        ids, orders_table = list(), list()
        order_products = dict()
        for order in orders_lst:
            if order[0] in ids:
                order_products[order[0]].append(order[6:])
            else:
                ids.append(order[0])
                orders_table.append(order[:5])
                order_products[order[0]] = []
                order_products[order[0]].append(order[6:])

        result_order_lst = []
        for order in orders_table:
            lst = []
            lst.append(order)
            lst.append(order_products[order[0]])
            result_order_lst.append(lst)

        result_dict['Orders_info'] = result_order_lst
        return result_dict

    def get_customer_from_login_and_password(self, login, password):
        select = self.tables['customer'].select().\
            where(self.tables['customer'].c.user_name == login).\
            where(self.tables['customer'].c.password == password)
        return self.connection.execute(select).fetchall()

    def update_category(self, cat_name_old, cat_name_new, image_new, description_new, slug_new, parent_id_new):
        update = self.tables['category'].update().returning(self.tables['category'])
        update = update.where(self.tables['category'].c.cat_name == cat_name_old).\
            values(cat_name=cat_name_new, image=image_new, description=description_new,
                   slug=slug_new, parent_id=parent_id_new)
        for cat_name_new in self.connection.execute(update):
            print(cat_name_new)

    def update_customer(self, email_old, new_user_name, new_password, new_phone, new_sh_addr):
        update = self.tables['customer'].update().returning(self.tables['customer'])
        update = update.where(self.tables['customer'].c.email == email_old).\
            values(user_name=new_user_name, password=new_password, phone=new_phone, shipping_address=new_sh_addr)
        for new_user_name in self.connection.execute(update):
            print(new_user_name)

    def update_product(self, old_prod_name, new_category_id, new_prod_name, new_image, new_description,
                       new_slug, new_price_ua, new_in_stock, new_other_info):
        update = self.tables['product'].update().returning(self.tables['product'])
        update = update.where(self.tables['product'].c.prod_name == old_prod_name).\
            values(category_id=new_category_id, prod_name=new_prod_name, image=new_image, description=new_description,
                   slug=new_slug, price_ua=new_price_ua, in_stock=new_in_stock, other_info=new_other_info)
        for new_category_id in self.connection.execute(update):
            print(new_category_id)

    def update_orders(self, order_id, new_customer_id, new_sum_price, new_delivery_data_time, new_payment_type, new_dict):
        update = self.tables['orders'].update().returning(self.tables['orders'])
        update = update.where(self.tables['orders'].c.id == order_id).\
            values(customer_id=new_customer_id, sum_price=new_sum_price, delivery_data_time=new_delivery_data_time,
                   payment_type=new_payment_type)
        for new_customer_id in self.connection.execute(update):
            print(new_customer_id)

        for key, value in new_dict.items():
            update = self.tables['order_products'].update().returning(self.tables['order_products'])
            update = update.where(self.tables['order_products'].c.orders_id == order_id).\
                values({'orders_id': order_id, 'product_id': key, 'number_prod': value})
            for some in self.connection.execute(update):
                print(some)

    def delete_customer(self, id_customer):
        select = self.tables['orders'].select().where(self.tables['orders'].c.customer_id == id_customer)
        result = self.connection.execute(select).fetchall()
        result_lst = [x[0] for x in result]

        for x in result_lst:
            self.delete_order(x)

        delete = self.tables['customer'].delete.where(self.tables['customer'].c.id == id_customer).\
            returning(self.tables['customer'])
        for id_customer in self.connection.execute(delete):
            print(id_customer)

    def delete_order(self, id_order):
        delete = self.tables['orders'].delete().returning(self.tables['orders'])
        delete = delete.where(self.tables['orders'].c.id == id_order)
        for id_order in self.connection.execute(delete):
            print(id_order)

        delete = self.tables['order_products'].delete().returning(self.tables['order_products'])
        delete = delete.where(self.tables['order_products'].c.orders_id == id_order)
        for id_order in self.connection.execute(delete):
            print(id_order)



conf = 'conf'
init_list = read_from_file(conf)

DB = DbSqlalQueries(init_list[0], init_list[1], init_list[2])
# DB.add_category('name_cat--', '//pass2//', '2description2', 'slug2', 1)
# DB.add_product(category_id=1, prod_name='phone2', image='//pass//', description='description', slug='//slug//2',
#                  price_ua=100, in_stock=25, other_info={})
# DB.add_customer(user_name='Denis2', email='2ralko2@gmail.com', password='2qwerty2',
#                   phone='0671663238', shipping_address='Kovalski2')
# DB.add_orders(customer_id=1, sum_price=777, delivery_data_time='2018-10-19 10:23:54+02',
#                 payment_type='card', dict={1: 1, 5: 40})
# DB.get_category().sort(key=lambda x: x[0])
# DB.get_parent_category_by_id(4)
DB.get_subcategories_by_id(1)
# DB.get_products_for_category(1)
# DB.get_orders_for_customer(1)
# DB.get_customer_from_login_and_password('Denis', 'qwerty')
# DB.delete_customer(1)

def test_get_parent_category_by_id():
    assert DB.get_parent_category_by_id(4) == [(4, 'Name3', '\\\\pass\\\\', 'description3', 'slug3', 2),
                                       (2, 'new_categorya', 'new_pass', 'TEXT OF DESCRIPTION', 'new_slug', 1),
                                       (1, 'categorya', 'pass', 'text', 'slug', None)]
