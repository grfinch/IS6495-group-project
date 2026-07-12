# Represents the person running the program, backed by a real account in
# the Customer or Employee table (see database_service.py).
#
# Employees get the full toolset: inventory management, restocking,
# creating bouquet types, discontinuing bouquet types, and selling bouquets.
#
# Customers get a simpler, read-only view of what's available, plus the
# ability to buy a bouquet.
#
# "buy" (customer) and "sell" (employee) are two menu labels for the same
# underlying DatabaseService.sell_bouquet() call - see database_service.py.
#
# Accounts are created/verified through register()/login(), which just
# wrap the matching DatabaseService methods (add_customer/add_employee and
# authenticate_customer/authenticate_employee). Neither of those ever
# hands back a password or its hash - only the account's public info -
# so a User object never holds a password in memory.


class User:
     def __init__(self, user_id: int = None, username: str = "", name: str = ""):
        self.user_id = user_id
        self.username = username
        self.name = name

    @property
    def role(self) -> str:
        raise NotImplementedError("Must implement from the derived class")

    def get_menu_options(self) -> dict:
        # Returns the {command: description} options this user type can see
        raise NotImplementedError("Must implement from the derived class")

    def can_access(self, user_selection: str) -> bool:
        # Anything not in this user's menu is off-limits to them
        return user_selection in self.get_menu_options()


class Employee(User):
    @property
    def role(self) -> str:
        return "Employee"

    def get_menu_options(self) -> dict:
        return {
            "flowers": "View flower inventory",
            "bouquets": "View types of bouquets you can create",
            "create": "Create a bouquet",
            "order": "Order more flowers",
            "sell": "Sell a bouquet",
            "discontinue": "Discontinue a bouquet type",
            "exit": "Exit program",
        }

    @classmethod
    def register(cls, db_service, username: str, password: str, name: str):
        # Returns a new Employee on success, or None if registration failed
        # (db_service already printed why - e.g. username taken).
        record = db_service.add_employee(username, password, name)
        if record is None:
            return None
        employee_id, db_username, db_name = record
        return cls(user_id=employee_id, username=db_username, name=db_name)
 
    @classmethod
    def login(cls, db_service, username: str, password: str):
        # Returns an Employee on success, or None if the username/password
        # didn't match anything.
        record = db_service.authenticate_employee(username, password)
        if record is None:
            return None
        employee_id, db_username, db_name = record
        return cls(user_id=employee_id, username=db_username, name=db_name)


class Customer(User):
     def __init__(self, user_id: int = None, username: str = "", name: str = "", email: str = None):
        super().__init__(user_id, username, name)
        self.email = email

    @property
    def role(self) -> str:
        return "Customer"

    def get_menu_options(self) -> dict:
        return {
            "flowers": "View available flowers",
            "bouquets": "View bouquets available to buy",
            "buy": "Buy a bouquet",
            "exit": "Exit program",
        }

    @classmethod
    def register(cls, db_service, username: str, password: str, name: str, email: str = None):
        record = db_service.add_customer(username, password, name, email)
        if record is None:
            return None
        customer_id, db_username, db_name, db_email = record
        return cls(user_id=customer_id, username=db_username, name=db_name, email=db_email)
 
    @classmethod
    def login(cls, db_service, username: str, password: str):
        record = db_service.authenticate_customer(username, password)
        if record is None:
            return None
        customer_id, db_username, db_name, db_email = record
        return cls(user_id=customer_id, username=db_username, name=db_name, email=db_email)
