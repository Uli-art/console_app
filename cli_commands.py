import inquirer
from db_connection import AppManagement


class ManagerCli:
    def __init__(self):
        self.app_manager = AppManagement()

    def run_app(self):
        while True:
            if self.app_manager.currUser is None:
                questions = [inquirer.List("unauthorized",
                                           choices=[("Authorization as user", "-u"), ("Authorization as manager", "-m"),
                                                    ("View all products", "-p"), ("Exit", "-e")])]
                answers = inquirer.prompt(questions).get("unauthorized")

                if answers == "-u" or answers == "-m":
                    self.registration(answers)
                elif answers == "-p":
                    self.print_all_products()
                else:
                    break
            elif self.app_manager.role == "-u" or self.app_manager.role == "-m":
                questions = [inquirer.List("actions",
                                           choices=[("View orders", "-o"), ("View products", "-p"),
                                                    ("Logout", "-l"), ("Exit", "-e")])]
                answers = inquirer.prompt(questions).get("actions")
                if answers == "-o":
                    self.view_all_orders()
                elif answers == "-p":
                    if self.app_manager.role == "-u":
                        self.view_all_products()
                    elif self.app_manager.role == "-m":
                        self.print_all_products()
                elif answers == "-l":
                    self.logout()
                else:
                    break
            elif self.app_manager.role == "-s":
                questions = [inquirer.List("actions",
                                           choices=[("View orders", "-o"), ("View products", "-p"),
                                                    ("View managers", "-m"), ("View logs", "-log"), ("Logout", "-l"), ("Exit", "-e")])]
                answers = inquirer.prompt(questions).get("actions")
                if answers == "-o":
                    self.view_all_orders()
                elif answers == "-p":
                    self.products_actions()
                elif answers == "-m":
                    self.view_all_managers()
                elif answers == "-log":
                    self.view_logs()
                elif answers == "-l":
                    self.logout()
                else:
                    break

    def registration(self, role):
        questions = [inquirer.List("registration_type",
                                   choices=[("Registration", "-r"), ("Login", "-l"), ("Go back", "-g")])]
        answers = inquirer.prompt(questions).get("registration_type")
        if answers == "-r":
            if role == "-u":
                self.user_registration()
            elif role == "-m":
                self.manager_registration()
        elif answers == "-l":
            self.login(role)

    def user_registration(self):
        questions = [
            inquirer.Text("name", message="Enter name"),
            inquirer.Text("email", message="Enter email"),
            inquirer.Text("password", message="Enter password")
        ]
        answers = inquirer.prompt(questions)
        self.app_manager.registration(answers.get('email'), answers.get('password'), "-u", answers.get('name'))

    def manager_registration(self):
        questions = [
            inquirer.Text("email", message="Enter email"),
            inquirer.Text("password", message="Enter password")
        ]
        answers = inquirer.prompt(questions)
        self.app_manager.registration(answers.get('email'), answers.get('password'), "-m")

    def login(self, role):
        questions = [
            inquirer.Text("email", message="Enter email"),
            inquirer.Text("password", message="Enter password")
        ]
        answers = inquirer.prompt(questions)
        self.app_manager.login(answers.get('email'), answers.get('password'), role)

    def logout(self):
        self.app_manager.logout()

    def print_all_products(self):
        self.app_manager.view_products()

    def view_all_products(self):
        self.app_manager.view_products()
        all_orders = self.app_manager.get_products()
        questions = [inquirer.List("products",
                                   choices=[*all_orders, ("Go back", "-g")])]
        answers = inquirer.prompt(questions).get("products")
        if self.app_manager.role == "-u":
            self.comments_actions(answers)

    def comments_actions(self, product_id):
        questions = [inquirer.List("action",
                                   choices=[("View comments", "-v"), ("Write comment", "-w"), ("Go back", "-g")])]
        answers = inquirer.prompt(questions).get("action")
        if answers =="-v":
            self.app_manager.currUser.view_comments(product_id)
        elif answers =="-w":
            self.write_comment(product_id)
        else:
            return

    def write_comment(self, product_id):
        questions = [
            inquirer.Text("rating", message="Enter rating"),
            inquirer.Text("text", message="Enter text")
        ]
        answers = inquirer.prompt(questions)
        self.app_manager.currUser.write_comment(product_id, answers.get("rating"), answers.get("text"))

    def view_comments(self, product_id):
        self.app_manager.currUser.view_comments(product_id)

    def products_actions(self):
        all_orders = self.app_manager.get_products()
        questions = [inquirer.List("products",
                                   choices=[*all_orders, ("Create product", "-c"), ("Go back", "-g")])]
        answers = inquirer.prompt(questions).get("products")
        if answers == "-g":
            return
        elif answers == "-c":
            if self.app_manager.role == "-m" or self.app_manager.role == "-s":
                self.create_product()
        self.view_products_actions(answers)

    def create_product(self):
        questions = [
            inquirer.Text("name", message="Enter name"),
            inquirer.List("type", message="Enter type", choices=[*self.app_manager.get_product_types()]),
            inquirer.Text("price", message="Enter price"),
            inquirer.Confirm("in_production", message="Is it in production?", default=True),
            inquirer.Text("image", message="Add image")
        ]
        answers = inquirer.prompt(questions)
        self.app_manager.currUser.create_product(answers.get("name"), answers.get("type"), answers.get("price"),
                                                 answers.get("in_production"), answers.get("image"))

    def view_products_actions(self, product_id):
        questions = [inquirer.List("actions",
                                   choices=[("Delete product", "-d"), ("Go back", "-g")])]
        answers = inquirer.prompt(questions).get("actions")
        if answers == "-d" and self.app_manager.role == "-s":
            self.app_manager.currUser.delete_product(product_id)
        else:
            return

    def view_logs(self):
        self.app_manager.currUser.view_logs()

    def get_orders_list(self):
        return self.app_manager.currUser.view_orders()

    def view_all_orders(self):
        all_orders = self.get_orders_list()
        questions = [inquirer.List("orders",
                                   choices=[*all_orders, ("Create order", "-c"), ("Go back", "-g")])]
        answers = inquirer.prompt(questions).get("orders")
        if answers == "-g":
            return
        elif answers == "-c":
            if self.app_manager.role == "-m" or self.app_manager.role == "-s":
                self.create_order_manager()
                self.view_orders_actions(answers)
            elif self.app_manager.role == "-u":
                self.create_order_user()
        else:
            if self.app_manager.role == "-m" or self.app_manager.role == "-s":
                self.view_orders_actions(answers)

    def create_order_user(self):
        questions = [
            inquirer.List("product", message="Enter product", choices=[*self.app_manager.get_products()]),
            inquirer.Text("quantity", message="Enter quantity"),
            inquirer.List("manager", message="Choose manager", choices=[*self.app_manager.get_managers()])
        ]
        answers = inquirer.prompt(questions)
        self.app_manager.currUser.create_order(answers.get("quantity"),  answers.get("manager"), answers.get("product"))

    def view_orders_actions(self, order_id):
        questions = [inquirer.List("actions",
                                   choices=[("Delete order", "-d"), ("Update status of order", "-u"), ("Go back", "-g")])]
        answers = inquirer.prompt(questions).get("actions")
        if answers == "-i":
            self.app_manager.currUser.view_manager_info(order_id)
        elif answers == "-d":
            self.app_manager.currUser.delete_order(order_id)
        elif answers == "-u":
            self.update_status_order(order_id)
        else:
            return

    def update_status_order(self, order_id):
        questions = [inquirer.List("statuses",
                                   choices=[*self.app_manager.get_statuses()])]
        answers = inquirer.prompt(questions).get("statuses")
        self.app_manager.currUser.update_order(order_id, answers)

    def create_order_manager(self):
        questions = [
            inquirer.List("product", message="Enter product", choices=[*self.app_manager.get_products()]),
            inquirer.Text("quantity", message="Enter quantity"),
            inquirer.List("user", message="Enter user", choices=[*self.app_manager.get_users()])
        ]
        answers = inquirer.prompt(questions)
        self.app_manager.currUser.create_order_manager(answers.get("quantity"),
                                                       answers.get("product"), answers.get("user"))

    def view_all_managers(self):
        all_managers = self.app_manager.currUser.view_managers()
        questions = [inquirer.List("managers",
                                   choices=[*all_managers, ("Go back", "-g")])]
        answers = inquirer.prompt(questions).get("managers")
        if answers == "-g":
            return
        self.view_managers_actions(answers)

    def view_managers_actions(self, manager_id):
        questions = [inquirer.List("actions",
                                   choices=[("View manager info", "-i"), ("Delete manager", "-d"),
                                            ("Change manager role", "-c"), ("Go back", "-g")])]
        answers = inquirer.prompt(questions).get("actions")
        if answers == "-i":
            self.app_manager.currUser.view_manager_info(manager_id)
        elif answers == "-d":
            self.app_manager.currUser.delete_manager(manager_id)
        elif answers == "-c":
            self.app_manager.currUser.change_manager_role(manager_id)
        else:
            return
