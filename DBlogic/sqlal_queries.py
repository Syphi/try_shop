import sqlalchemy as sa


class DbSqlalQueries():

    def __init__(self):
        try:
            self.db_string = "postgresql://postgres:revo1917@localhost/shop"
            self.db = sa.create_engine(self.db_string)
            self.connection = self.db.connect()
            self.metadata = sa.MetaData()
            self.orders = sa.Table('orders', self.metadata, autoload=True, autoload_with=self.db)
            self.customer = sa.Table('customer', self.metadata, autoload=True, autoload_with=self.db)
            self.product = sa.Table('product', self.metadata, autoload=True, autoload_with=self.db)
            self.category = sa.Table('category', self.metadata, autoload=True, autoload_with=self.db)
            self.order_products = sa.Table('order_products', self.metadata, autoload=True, autoload_with=self.db)
            print('Init class and connection')
        except Exception as e:
            print('shit - no such db')
            print(e)

    def __del__(self):
        self.connection.close()
        print('Close class and connection')

    def add_category(self, cat_name, image_pass, description, slug, parent_id):
        insert = sa.insert(self.category)
        insert = insert.values({'cat_name': str(cat_name), 'image': str(image_pass), 'description': str(description),
                                'slug': str(slug), 'parent_id': parent_id})
        self.connection.execute(insert)

    def add_product(self, category_id, prod_name, image, description, slug, price_ua, in_stock, other_info):
        insert = sa.insert(self.product)
        insert = insert.values({'category_id': category_id, 'prod_name': str(prod_name), 'image': str(image),
                               'description': str(description), 'slug': str(slug), 'price_ua': price_ua,
                               'in_stock': in_stock, 'other_info': other_info})
        self.connection.execute(insert)

    def add_customer(self, user_name, email, password, phone, shipping_address):
        insert = sa.insert(self.customer)
        insert = insert.values({'user_name': str(user_name), 'email': str(email), 'password': str(password),
                                'phone': phone, 'shipping_address': shipping_address})
        self.connection.execute(insert)

    def add_orders(self, customer_id, sum_price, delivery_data_time, payment_type, dict):
        # add to orders table
        insert = sa.insert(self.orders)
        insert = insert.values({'customer_id': customer_id, 'sum_price': sum_price,
                                'delivery_data_time': delivery_data_time, 'payment_type': payment_type})
        self.connection.execute(insert)

        # select last id in orders table
        select = self.orders.select()
        select = select.where(sa.and_(self.orders.c.customer_id == customer_id,
                                      self.orders.c.sum_price == sum_price,
                                      # self.orders.c.delivery_date_time == delivery_data_time, //how to
                                      self.orders.c.payment_type == payment_type))
        result_id = self.connection.execute(select).fetchall()
        result_id = result_id[-1][0]

        print(result_id)
        print(dict)

        # add to orders_product name
        insert = self.order_products.insert()
        insert_list = []
        for key, value in dict.items():
            print(result_id, key, value)
            new_row = {'orders_id': result_id, 'product_id': key, 'number_prod': value}
            insert_list.append(new_row)

        print(insert_list)
        self.connection.execute(insert, insert_list)

    def get_category(self):
        select = self.category.select()
        result = self.connection.execute(select).fetchall()
        print(result)
        return result

    def get_subcategory(self, category_id):
        select = self.category.select()
        select = select.where(self.category.c.id == category_id)
        result = self.connection.execute(select).fetchall()

        result_lst = []
        result_lst.append(result[0])
        while result[0][-1] != None:
            select = self.category.select()
            select = select.where(self.category.c.id == result[0][-1])
            result = result = self.connection.execute(select).fetchall()
            result_lst.append(result[0])
        print(result_lst)
        return result_lst

    def get_products_for_category(self, category_id):
        select = self.product.select()
        select = select.where(self.product.c.category_id == category_id)
        return self.connection.execute(select).fetchall()

    def get_orders_for_customer(self, customer_id):
        '''
        need to give customer and order info
        use 3 tables customer, orders, order_products

        join with orders.id == orders_products.orders_id
        :return: dict{{'Client_info': (id, user_name, email, password, phone, addres),
        'Order_info': [(order.id, order.customer_id, order.sum_price, order.datetime, order.payment_type) ]}

        '''
        select = self.customer.select().\
            where(self.customer.c.id == customer_id)
        client_info = self.connection.execute(select).fetchall()[0]

        result_dict = {'Client_info': client_info}

        join = self.orders.join(self.order_products,
                                self.orders.c.id == self.order_products.c.orders_id)
        result = sa.select([self.orders, self.order_products]).select_from(join)
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
            print(order)
            lst.append(order)
            lst.append(order_products[order[0]])
            result_order_lst.append(lst)

        result_dict['Orders_info'] = result_order_lst
        return result_dict

    def get_customer_from_login_and_password(self, login, password):
        select = self.customer.select().\
            where(self.customer.c.user_name == login).\
            where(self.customer.c.password == password)
        return self.connection.execute(select).fetchall()

    def update_category(self, cat_name_old, cat_name_new, image_new, description_new, slug_new, parent_id_new):
        update = self.category.update()
        update = update.where(self.category.c.cat_name == cat_name_old).\
            values(cat_name=cat_name_new, image=image_new, description=description_new,
                   slug=slug_new, parent_id=parent_id_new)
        self.connection.execute(update)

    def update_customer(self, email_old, new_user_name, new_password, new_phone, new_sh_addr):
        update = self.customer.update()
        update = update.where(self.customer.c.email == email_old).\
            values(user_name=new_user_name, password=new_password, phone=new_phone, shipping_address=new_sh_addr)
        self.connection.execute(update)

    def update_product(self, old_prod_name , new_category_id, new_prod_name, new_image, new_description,
                       new_slug, new_price_ua, new_in_stock, new_other_info):
        update = self.product.update()
        update = update.where(self.product.c.prod_name == old_prod_name).\
            values(category_id=new_category_id, prod_name=new_prod_name, image=new_image, description=new_description,
                   slug=new_slug, price_ua=new_price_ua, in_stock=new_in_stock, other_info=new_other_info)
        self.connection.execute(update)

    def update_orders(self, order_id, new_customer_id, new_sum_price, new_delivery_data_time, new_payment_type, new_dict):
        update = self.orders.update()
        update = update.where(self.orders.c.id == order_id).\
            values(customer_id=new_customer_id, sum_price=new_sum_price, delivery_data_time=new_delivery_data_time,
                   payment_type=new_payment_type)
        self.connection.execute(update)

        for key, value in new_dict.items():
            update = self.order_products.update()
            update = update.where(self.order_products.c.orders_id == order_id).\
                values({'orders_id': order_id, 'product_id': key, 'number_prod': value})
            self.connection.execute(update)

    def delete_customer(self, id_customer):
        select = self.orders.select().where(self.orders.c.customer_id == id_customer)
        result = self.connection.execute(select).fetchall()
        result_lst = []
        result_lst = [x[0] for x in result]
        print(result_lst)

        for x in result_lst:
            self.delete_order(x)

        delete = self.customer.delete.where(self.customer.c.id == id_customer)
        self.connection.execute(delete)

    def delete_order(self, id_order):
        delete = self.orders.delete()
        delete = delete.where(self.orders.c.id == id_order)
        self.connection.execute(delete)

        delete = self.order_products.delete()
        delete = delete.where(self.order_products.c.orders_id == id_order)
        self.connection.execute(delete)


test = DbSqlalQueries()
# test.add_category('name2', '//pass2//', '2description2', 'slug2', 1)
# test.add_product(category_id=1, prod_name='phone2', image='//pass//', description='description', slug='//slug//2',
#                  price_ua=100, in_stock=25, other_info={})
# test.add_customer(user_name='Denis2', email='2ralko2@gmail.com', password='2qwerty2',
#                   phone='0671663238', shipping_address='Kovalski2')
# test.add_orders(customer_id=1, sum_price=777, delivery_data_time='2018-10-19 10:23:54+02',
#                 payment_type='cash', dict={1: 1, 5: 40})cd
# test.get_category().sort(key=lambda x: x[0])
# test.get_subcategory(4)
# test.get_products_for_category(1)
# test.get_orders_for_customer(1)
# test.get_customer_from_login_and_password('Denis', 'qwerty')
# test.delete_customer(1)


# Pass
# add_category
# add_product
# add_customer
# add_orders
# get_category
# products_for_category
# orders_for_customer
# get_customer_from_login_and_password
# get_subcategories



# Need to do
# Update
# Delete