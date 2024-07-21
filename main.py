from cli_commands import ManagerCli


if __name__ == "__main__":
    app = ManagerCli()
    app.run_app()
    # app = AppManagement()
    # app.login('john@example.com', 'password123', '-u')
    # app.view_products()
    # #print(app.currUser.email)
    # app.login('David@gmail.com', 'password5', '-m')
    # print(app.currUser.view_orders())
    # app.logout()
    # print(app.currUser)
