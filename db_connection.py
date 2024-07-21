import psycopg2
from tabulate import tabulate


class AppManagement:
    def __init__(self):
        self.currUser = None
        self.role = None
        try:
            self.conn = psycopg2.connect(dbname='ToyFactory', user='postgres', password='1958', host='127.0.0.1')
        except:
            print('Can`t establish connection to database')

    def __del__(self):
        self.conn.close()

    def registration(self, email, password, role, name=''):
        try:
            with self.conn.cursor() as curs:
                if role == "-u":
                    curs.execute('CALL add_user(%s, %s, %s)', (name, email, password,))
                    self.currUser = User(name, email, password)
                elif role == "-m":
                    curs.execute('CALL add_manager(%s, %s)', (email, password,))
                    self.currUser = Manager(email, password)
                self.role = role
            self.conn.commit()
        except:
            print('Registration fail!')
            self.reconnect()

    def login(self, email, password, role):
        try:
            with self.conn.cursor() as curs:
                if role == "-u":
                    curs.execute('SELECT "name", email, "password" FROM "user" WHERE email=%s AND password=%s',
                                 (email, password,))
                    logged_user = curs.fetchone()
                    self.currUser = User(*logged_user)
                    self.role = role
                elif role == "-m":
                    curs.execute('SELECT email, "password" FROM "manager" WHERE email=%s AND password=%s',
                                 (email, password,))
                    logged_manager = curs.fetchone()
                    curs.execute('SELECT is_admin FROM "manager" WHERE email=%s AND password=%s',
                                 (email, password,))
                    is_admin = curs.fetchone()
                    if is_admin[0]:
                        self.currUser = SuperUser(*logged_manager)
                        self.role = "-s"
                    else:
                        self.currUser = Manager(*logged_manager)
                        self.role = role
        except:
            print('Login fail!')
            self.reconnect()

    def logout(self):
        self.currUser = None

    def view_products(self):
        try:
            with self.conn.cursor() as curs:
                curs.execute('SELECT * FROM all_products')
                all_products = curs.fetchall()
                print(tabulate(all_products, headers=["Id", "Name", "Price", "Type", "In_production", "Image"]))
        except:
            print('Something go wrong!')
            self.reconnect()

    def get_products(self):
        try:
            with self.conn.cursor() as curs:
                curs.execute('SELECT "name", "id" FROM all_products')
                all_products = curs.fetchall()
                return all_products
        except:
            print('Something go wrong!')
            self.reconnect()

    def get_users(self):
        try:
            with self.conn.cursor() as curs:
                curs.execute('SELECT "email", "id" FROM "user"')
                all_users = curs.fetchall()
                return all_users
        except:
            print('Something go wrong!')
            self.reconnect()

    def get_managers(self):
        try:
            with self.conn.cursor() as curs:
                curs.execute('SELECT "email", "id" FROM "manager"')
                all_managers = curs.fetchall()
                return all_managers
        except:
            print('Something go wrong!')
            self.reconnect()

    def get_statuses(self):
        try:
            with self.conn.cursor() as curs:
                curs.execute('SELECT "status", "id" FROM "status"')
                all_statuses = curs.fetchall()
                return all_statuses
        except:
            print('Something go wrong!')
            self.reconnect()

    def get_product_types(self):
        try:
            with self.conn.cursor() as curs:
                curs.execute('SELECT "type", "id" FROM "product_type"')
                all_types = curs.fetchall()
                return all_types
        except:
            print('Something go wrong!')
            self.reconnect()

    def reconnect(self):
        self.conn.close()
        self.conn = psycopg2.connect(dbname='ToyFactory', user='postgres', password='1958', host='127.0.0.1')


class User:
    def __init__(self,  *params):
        if len(params) == 3:
            self.name = params[0]
            self.email = params[1]
            self.password = params[2]
        elif len(params) == 2:
            self.email = params[0]
            self.password = params[1]
        try:
            self.conn = psycopg2.connect(dbname='ToyFactory', user='postgres', password='1958', host='127.0.0.1')
        except:
            print('Can`t establish connection to database')

    def reconnect(self):
        self.conn.close()
        self.conn = psycopg2.connect(dbname='ToyFactory', user='postgres', password='1958', host='127.0.0.1')

    def view_products(self):
        try:
            with self.conn.cursor() as curs:
                curs.execute('SELECT * FROM all_products')
                all_products = curs.fetchall()
                print(tabulate(all_products, headers=["Id", "Name", "Price", "Type", "In_production", "Image"]))
        except:
            print('Something go wrong!')
            self.reconnect()

    def view_orders(self):
        try:
            with self.conn.cursor() as curs:
                curs.execute('SELECT * FROM all_orders WHERE user_email=%s', (self.email, ))
                all_orders = curs.fetchall()
                print(tabulate(all_orders,
                               headers=["Id","Date", "Completion_date", "Quantity", "Manager_email",
                                        "Product_name", "Status", "User_email"]))
                return all_orders
        except:
            print('Something go wrong!')
            self.reconnect()

    def view_comments(self, product_id):
        try:
            with self.conn.cursor() as curs:
                curs.execute('SELECT rating, text, "date" FROM review WHERE product_id=%s', (product_id,))
                all_comments = curs.fetchall()
                print(tabulate(all_comments, headers=["Rating", "Text", "Date"]))
        except:
            print('Something go wrong!')
            self.reconnect()

    def write_comment(self, product_id, rating, text):
        try:
            with self.conn.cursor() as curs:
                curs.execute('SELECT "id" FROM "user" WHERE email=%s',
                             (self.email,))
                user_id = curs.fetchone()
                curs.execute('CALL add_review(%s, %s, %s, %s)', (user_id[0], product_id, rating, text,))
            self.conn.commit()
        except:
            print('Something go wrong!')
            self.reconnect()

    def create_order(self, new_quantity, new_manager_id, new_product_id):
        try:
            with self.conn.cursor() as curs:
                curs.execute('SELECT "id" FROM "user" WHERE email=%s', (self.email,))
                user_id = curs.fetchone()
                curs.execute('CALL add_order(CAST(now() AS DATE), NULL, %s, %s, %s, 1, %s)',
                                (new_quantity, new_manager_id, new_product_id, user_id[0],))
                print("Create order")
            self.conn.commit()
        except:
            print('Something go wrong!')
            self.reconnect()


class Manager(User):
    def __init__(self,  email, password):
        super().__init__(email, password)

    def reconnect(self):
        self.conn.close()
        self.conn = psycopg2.connect(dbname='ToyFactory', user='postgres', password='1958', host='127.0.0.1')

    def view_orders(self):
        try:
            with self.conn.cursor() as curs:
                curs.execute('SELECT * FROM all_orders WHERE manager_email=%s order by "id"', (self.email, ))
                all_orders = curs.fetchall()
                print(tabulate(all_orders,
                               headers=["Id", "Date", "Completion_date", "Quantity", "Manager_email",
                                        "Product_name", "Status", "User_email"]))
                choices = []
                for i in range(len(all_orders)):
                    choices.append((str(all_orders[i][3]) + " " + str(all_orders[i][4]) + " " +
                                    str(all_orders[i][5]) + " " + str(all_orders[i][6]), all_orders[i][0]))
                return choices
        except:
            print('Something go wrong!')
            self.reconnect()

    def delete_order(self, order_id):
        try:
            with self.conn.cursor() as curs:
                curs.execute('SELECT "id" FROM "manager" WHERE email=%s', (self.email,))
                manager_id = curs.fetchone()
                curs.execute('DELETE FROM "order" WHERE "id"=%s AND manager_id=%s', (order_id, manager_id))
            self.conn.commit()
        except:
            print('Cant delete order!')
            self.reconnect()

    def update_order(self, order_id, new_status_id):
        try:
            with self.conn.cursor() as curs:
                curs.execute('CALL update_order(%s, NULL, NULL, NULL, NULL, NULL, %s, NULL)',
                             (order_id, new_status_id))
                print("Update order")
            self.conn.commit()
        except:
            print('Cant update order!')
            self.reconnect()

    def create_order_manager(self, new_quantity, new_product_id, new_user_id):
        try:
            with self.conn.cursor() as curs:
                curs.execute('SELECT "id" FROM "manager" WHERE email=%s',
                                 (self.email,))
                manager_id = curs.fetchone()
                curs.execute('CALL add_order(CAST(now() AS DATE), NULL, %s, %s, %s, 1, %s)',
                             (new_quantity, manager_id[0], new_product_id, new_user_id,))
                print("Create order")
            self.conn.commit()
        except:
            print('Cant create order!')
            self.reconnect()


class SuperUser(Manager):
    def __init__(self, email, password):
        super().__init__(email, password)

    def reconnect(self):
        self.conn.close()
        self.conn = psycopg2.connect(dbname='ToyFactory', user='postgres', password='1958', host='127.0.0.1')

    def create_product(self, name,  product_type, price, in_production, image):
        try:
            with self.conn.cursor() as curs:
                curs.execute('CALL add_product(%s, %s, %s, %s, %s)', (name,  product_type, price, in_production, image,))
                print("Create product %s", (name,))
            self.conn.commit()
        except:
            print('Cant create product!')
            self.reconnect()

    def delete_product(self, product_id):
        try:
            with self.conn.cursor() as curs:
                curs.execute('DELETE FROM product WHERE "id"=%s', (product_id,))
                print("Delete product with id=%s", (product_id,))
            self.conn.commit()
        except:
            print('Cant delete product!')
            self.reconnect()

    def update_product(self, product_id, name, price, product_type, in_production, image):
        try:
            with self.conn.cursor() as curs:
                curs.execute('CALL update_product(%s, %s, %s, %s, %s, %s)',
                             (product_id, name, product_type, price, in_production, image))
                print("Update product %s", (name,))
            self.conn.commit()
        except:
            print('Cant update product!')
            self.reconnect()

    def view_managers(self):
        try:
            with self.conn.cursor() as curs:
                curs.execute('SELECT email, "id" FROM manager')
                all_managers = curs.fetchall()
                print(tabulate(all_managers, headers=["Email"]))
                return all_managers
        except:
            print('Cant view managers!')
            self.reconnect()

    def view_manager_info(self, manager_id):
        try:
            with self.conn.cursor() as curs:
                curs.execute('SELECT "name", surname, phone_number, resume FROM manager_info WHERE "id"=%s',
                             (manager_id,))
                manager_info = curs.fetchall()
                print(tabulate(manager_info, headers=["Name", "Surname", "Phone_number", "Resume"]))
        except:
            print('Cant view manager info!')
            self.reconnect()

    def delete_manager(self, manager_id):
        try:
            with self.conn.cursor() as curs:
                curs.execute('CALL delete_manager(%s)', (manager_id,))
            self.conn.commit()
        except:
            print('Cant delete manager!')
            self.reconnect()

    def change_manager_role(self, manager_id):
        try:
            with self.conn.cursor() as curs:
                curs.execute('CALL change_role(%s)', (manager_id,))
                print("Change manager role")
            self.conn.commit()
        except:
            print('Cant change manager role!')
            self.reconnect()

    def view_orders(self):
        try:
            with self.conn.cursor() as curs:
                curs.execute('SELECT * FROM all_orders')
                all_orders = curs.fetchall()
                print(tabulate(all_orders,
                                headers=["Id", "Date", "Completion_date", "Quantity", "Manager_email",
                                            "Product_name", "Status", "User_email"]))
                choices = []
                for i in range(len(all_orders)):
                    choices.append((str(all_orders[i][3]) + " " + str(all_orders[i][4]) + " " +
                                    str(all_orders[i][5]) + " " + str(all_orders[i][6]), all_orders[i][0]))
                return choices
        except:
            print('Something go wrong!')
            self.reconnect()

    def view_products(self):
        try:
            with self.conn.cursor() as curs:
                curs.execute('SELECT * FROM all_products')
                all_products = curs.fetchall()
                print(tabulate(all_products, headers=["Id", "Name", "Price", "Type", "In_production", "Image"]))
        except:
            print('Something go wrong!')
            self.reconnect()

    def view_logs(self):
        try:
            with self.conn.cursor() as curs:
                curs.execute('SELECT * FROM log')
                all_logs = curs.fetchall()
                print(tabulate(all_logs, headers=["Id", "Activity", "Date", "User id"]))
        except:
            print('Something go wrong!')
            self.reconnect()

    def delete_order(self, order_id):
        try:
            with self.conn.cursor() as curs:
                curs.execute('DELETE FROM "order" WHERE "id"=%s', (order_id,))
            self.conn.commit()
        except:
            print('Cant delete order!')
            self.reconnect()
