import getpass

from flower import Flower
from bouquet import Bouquet
from database_service import DatabaseService
from user import User, Customer, Employee

# present the user with options:
#   view flower inventory
#   view types of bouquets they can create
#   attempt to create a bouquet
#   order more flowers
#   <think of some way to incorporate different user types>
#       Employee: orders flowers and creates bouquets?
#       Customer: can view available bouquets and buy some

# Employee vs Customer is handled by the User/Employee/Customer classes
# in user.py, each backed by a real row in the Customer or Employee table.
# At startup we ask which type of account this is, then log in or register,
# then use that user's own menu_options for the rest of the session.
#
# Employee-ish:  full inventory view (ids/stock), restock ("order"),
#                add flower, create bouquet type, discontinue bouquet, sell
# Customer-ish:  flowers as name + price only, bouquets with recipes, buy


class Project:

    def prompt_for_user(self, flower_shop):
        # Ask once at startup: employee or customer, then log in or
        # register. Loops until a real account is found/created.
        while True:
            action = input("Do you have an account? (login/register): ").lower().strip()
            if action not in ("login", "register"):
                print("Please type 'login' or 'register'.")
                continue

            username = input("Username: ").strip()
            # getpass hides the password as it's typed. Falls back to a normal (visible) prompt if the terminal doesn't support it.
            try:
                password = getpass.getpass("Password: ")
            except Exception:
                password = input("Password: ")

            if action == "login":
                user = User.login(flower_shop, username, password)
                if user is None:
                    print("Invalid username or password.")
                    continue
                return user
            else:  # register
                account_type = (
                    input("Are you an employee or a customer? (employee/customer): ")
                    .lower()
                    .strip()
                )
                if account_type not in ("employee", "customer"):
                    print("Please type 'employee' or 'customer'.")
                    continue

                name = input("Enter your full name: ").strip()
                email = input("Enter your email (optional): ").strip() or None
                user = User.register(
                    flower_shop,
                    username,
                    password,
                    name,
                    email,
                    account_type == "employee",
                )

                if user is None:
                    # flower_shop already printed why (e.g. username taken)
                    continue
                return user

    def run(self):

        # One DatabaseService/connection for the whole session
        flower_shop = DatabaseService()

        current_user = self.prompt_for_user(flower_shop)

        # Menu options come from the user's role (Employee vs Customer),
        # defined in user.py. Keys are what the user types, values are
        # the descriptions.
        menu_options = current_user.get_menu_options()

        ################
        # Welcome banner#
        ################

        print("=" * 55)
        print("          🌸  Welcome to the Flower Shop  🌸")
        print(f"   Logged in as: {current_user.name} ({current_user.role})")
        print("=" * 55)

        # Menu loop, repeats until user types exit

        user_selection = ""
        while user_selection != "exit":
            # Show the option list each time through the loop
            print("\n" + "-" * 55)
            print("              *** Option List ***")
            for key, value in menu_options.items():
                # pads the key to 12 characters so the menu lines up
                print(f"  [{key:<15}] {value}")
            print("-" * 55)

            user_selection = input("Enter an option: ").lower()

            # Guard against typing a command that isn't in this user's menu (e.g. a customer typing "order" or "discontinue")
            if user_selection != "exit" and not current_user.can_access(user_selection):
                print("Invalid selection, please try again.")
                continue

            if user_selection == "flowers":
                # Rows come back as flower_id, name, color, price, stock)
                results = flower_shop.fetch_flower()
                if isinstance(current_user, Employee):
                    # Employees see ids and stock (needed for "order"/"create")
                    for item in results:
                        print(
                            f"  {item[0]:>3} | {item[2]} {item[1]} - ${item[3]:.2f} - {item[4]} in stock"
                        )
                else:
                    # Customers see name and price only
                    for item in results:
                        print(f"  {item[2]} {item[1]} - ${item[3]:.2f}")
                input("Press return to continue...")

            elif user_selection == "bouquets":
                # Show every bouquet and the flowers inside it
                bouquets = flower_shop.fetch_bouquet()
                for bouquet in bouquets:
                    print(f"\n  {bouquet[1]}:")  # bouquet name
                    # Recipe rows: (name, color, price, quantity)
                    recipe = flower_shop.fetch_bouquet_recipe(bouquet[0])
                    for ingredient in recipe:
                        print(
                            f"      {ingredient[3]} x {ingredient[1]} {ingredient[0]} (${ingredient[2]:.2f} each)"
                        )
                input("\nPress return to continue...")

            elif user_selection == "create":
                # Show flowers so the user knows the ids
                results = flower_shop.fetch_flower()
                # prints one flower per row
                for item in results:
                    print(f"  {item[0]:>3} | {item[2]} {item[1]} - ${item[3]:.2f}")

                try:
                    name = input("Enter a name for the new bouquet: ")

                    # Collect the recipe: which flowers and how many of each
                    flowers_and_quantity = {}
                    another = "y"
                    while another == "y":
                        flower_id = int(input("Enter a flower id: "))
                        # Check the flower exists before adding it to the recipe
                        if flower_shop.fetch_flower(flower_id) is None:
                            print("That flower id doesn't exist, try again.")
                            continue
                        quantity = int(input("How many of this flower? "))
                        flowers_and_quantity[flower_id] = quantity
                        another = input("Add another flower? (y/n) ").lower()

                    # Build the bouquet object and save it to the database
                    new_bouquet = Bouquet(name, flowers_and_quantity)
                    flower_shop.add_bouquet(new_bouquet)
                except ValueError:
                    print("Please enter numbers only.")
                input("Press return to continue...")

            elif user_selection == "order":
                # Show inventory with ids so the user knows what to order
                results = flower_shop.fetch_flower()
                for item in results:
                    print(f"  {item[0]:>3} | {item[2]} {item[1]} - {item[4]} in stock")

                try:
                    flower_id = int(input("Enter the flower id to order: "))
                    amount = int(input("Enter how many to add: "))
                    flower_shop.increase_stock(flower_id, amount)

                    # Show the updated flower so the user sees it worked
                    updated = flower_shop.fetch_flower(flower_id)
                    print(
                        f"Updated: {updated[2]} {updated[1]} now has {updated[4]} in stock"
                    )
                except ValueError:
                    print("Please enter numbers only.")
                input("Press return to continue...")

            elif user_selection in ("buy", "sell"):
                # Same feature either way: pull the flowers needed for one
                # bouquet out of inventory. Customers see it as "buy",
                # employees see it as "sell".
                bouquets = flower_shop.fetch_bouquet()
                for bouquet in bouquets:
                    price = flower_shop.calculate_bouquet_price(bouquet[0])
                    print(f"  {bouquet[0]:>3} | {bouquet[1]} - ${price:.2f}")

                try:
                    bouquet_id = int(input("Enter the bouquet id: "))
                    if flower_shop.fetch_bouquet(bouquet_id) is None:
                        print("That bouquet id doesn't exist.")
                    elif not flower_shop.can_make_bouquet(bouquet_id):
                        print(
                            "Sorry, we don't have enough flowers in stock for that bouquet right now."
                        )
                    else:
                        price = flower_shop.calculate_bouquet_price(bouquet_id)
                        confirm = input(
                            f"This bouquet costs ${price:.2f}, confirm? (y/n) "
                        ).lower()
                        if confirm == "y":
                            flower_shop.sell_bouquet(bouquet_id)
                        else:
                            print("Purchase cancelled")
                except ValueError:
                    print("Please enter numbers only.")
                input("Press return to continue...")

            elif user_selection == "discontinue":
                # Show bouquets so the user knows the ids
                bouquets = flower_shop.fetch_bouquet()
                for bouquet in bouquets:
                    print(f"  {bouquet[0]:>3} | {bouquet[1]}")

                try:
                    bouquet_id = int(input("Enter the bouquet id to discontinue: "))
                    confirm = input(
                        "This will permanently remove the bouquet, continue? (y/n) "
                    ).lower()
                    if confirm == "y":
                        flower_shop.delete_bouquet(bouquet_id)
                    else:
                        print("Discontinue aborted")
                except ValueError:
                    print("Please enter numbers only.")
                input("Press return to continue...")

            elif user_selection == "add customer":
                username = input("New customer's username: ").strip()
                # Hide the password as it's typed, same as the login prompt
                try:
                    password = getpass.getpass("New customer's password: ")
                except Exception:
                    password = input("New customer's password: ")
                name = input("New customer's full name: ").strip()
                email = input("New customer's email (optional): ").strip() or None

                # add_customer prints its own success/failure message
                flower_shop.add_user(username, password, name, email)
                input("Press return to continue...")

            elif user_selection == "remove customer":
                customers = flower_shop.fetch_user()
                for customer in customers:
                    # customer = (customer_id, username, name, email)
                    print(f"  {customer[0]:>3} | {customer[1]} - {customer[2]}")

                try:
                    customer_id = int(input("Enter the customer id to remove: "))
                    if flower_shop.fetch_customer(customer_id) is None:
                        print("That customer id doesn't exist.")
                    else:
                        confirm = input(
                            "This will permanently delete the account, continue? (y/n) "
                        ).lower()
                        if confirm == "y":
                            flower_shop.delete_customer(customer_id)
                        else:
                            print("Removal cancelled")
                except ValueError:
                    print("Please enter numbers only.")
                input("Press return to continue...")

            else:
                # Only show the error if the input wasn't "exit"
                if user_selection != "exit":
                    print("Invalid selection, please try again.")

        print("\nThanks for visiting the Flower Shop! 🌸")


project = Project()
project.run()
