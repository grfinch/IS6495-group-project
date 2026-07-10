# Represents the person running the program.
#
# Employees get the full toolset: inventory management, restocking,
# creating bouquet types, discontinuing bouquet types, and selling bouquets.
#
# Customers get a simpler, read-only view of what's available, plus the
# ability to buy a bouquet.
#
# "buy" (customer) and "sell" (employee) are two menu labels for the same
# underlying DatabaseService.sell_bouquet() call - see database_service.py.


class User:
    def __init__(self, name: str = ""):
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


class Customer(User):
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


def create_user(user_type: str, name: str = "") -> User:
    # Small factory so main.py doesn't need to import Employee/Customer directly
    normalized = user_type.strip().lower()
    if normalized == "employee":
        return Employee(name)
    elif normalized == "customer":
        return Customer(name)
    else:
        raise ValueError(f"Unknown user type: {user_type!r}")
