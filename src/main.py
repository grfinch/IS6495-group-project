import getpass

from flower import Flower
from bouquet import Bouquet
from database_service import DatabaseService

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
            account_type = input("Are you an employee or a customer? (employee/customer): ").lower().strip()
            if account_type not in ("employee", "customer"):
                print("Please type 'employee' or 'customer'.")
                continue
 
            user_class = Employee if account_type == "employee" else Customer
 
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
                user = user_class.login(flower_shop, username, password)
                if user is None:
                    print("Invalid username or password.")
                    continue
                return user
 
            else:  # register
                name = input("Enter your full name: ").strip()
                if user_class is Customer:
                    email = input("Enter your email (optional): ").strip() or None
                    user = Customer.register(flower_shop, username, password, name, email)
                else:
                    user = Employee.register(flower_shop, username, password, name)
 
                if user is None:
                    # flower_shop already printed why (e.g. username taken)
                    continue
                return user

    def run(self):

        # One DatabaseService/connection for the whole session
        flower_shop = DatabaseService()
 
        current_user = self.prompt_for_user(flower_shop)
        menu_options = current_user.get_menu_options()

        # The keys are what the user types, the values are the descriptions
        menu_options = {"flowers": "View flower inventory",
                        "bouquets": "View types of bouquets you can create",
                        "create": "Create a bouquet",
                        "order": "Order more flowers",
                        "discontinue": "Discontinue a bouquet type",
                        "exit": "Exit program"
                        }
        
        # TODO (Anna): user types (Employee vs Customer) - this section is yours!
        # Leaving some notes from what I noticed while building the menu,
        # in case they're useful - but totally your call how to design it :)
        #
        # While wiring up the options I noticed they naturally split:
        #   Employee-ish:  full inventory view (ids/stock), restock ("order"),
        #                  add flower, create bouquet type, discontinue bouquet
        #   Customer-ish:  flowers as name + price only, bouquets with recipes,
        #                  buy a bouquet (see note below)
        #
        # NOTE: "buy a bouquet" is not built yet. It's the same feature as
        # "sell a bouquet" in Gaven's TODO list in database_service.py -
        # one feature, mentioned in two places, built by nobody so far :)
        # 
        #
        # One idea for the roles: ask "employee or customer?" once at startup,
        # then show a different menu_options dictionary per role. But if you
        # have a better approach, go for it!
        

        ################
        #Welcome banner#
        ################
      
        print("=" * 40)
        print("   🌸  Welcome to the Flower Shop  🌸")
        print("=" * 40)

     
        # Menu loop, repeats until user types exit 
        
        user_selection = ""
        while user_selection != "exit":
            # Show the option list each time through the loop
            print("\n" + "-" * 40)
            print("*** Option List ***")
            for key, value in menu_options.items():
                # pads the key to 12 characters so the menu lines up
                print(f"  [{key:<12}] {value}")
            print("-" * 40)

            user_selection = input("Enter an option: ").lower()

            # Guard against typing a command that isn't in this user's menu (e.g. a customer typing "order" or "discontinue")
            if user_selection != "exit" and not current_user.can_access(user_selection):
                print("Invalid selection, please try again.")
                continue

            # Create the database service to handle all DB interactions
            flower_shop = DatabaseService()

            if user_selection == "flowers":
                # Show the full inventory with ids, prices, and stock
                results = flower_shop.fetch_flower()
                for item in results:
                    print(f"  {item[0]:>3} | {item[2]} {item[1]} - ${item[3]:.2f} - {item[4]} in stock")
                input("Press return to continue...")

            elif user_selection == "bouquets":
                # Show every bouquet and the flowers inside it
                bouquets = flower_shop.fetch_bouquet()
                for bouquet in bouquets:
                    print(f"\n  {bouquet[1]}:")   # bouquet name
                    recipe = flower_shop.fetch_bouquet_recipe(bouquet[0])
                    for ingredient in recipe:
                        # example: 12 x Red Rose ($2.50 each)
                        print(f"      {ingredient[3]} x {ingredient[1]} {ingredient[0]} (${ingredient[2]:.2f} each)")
                input("\nPress return to continue...")

            elif user_selection == "create":
                # Show flowers so the user knows the ids
                results = flower_shop.fetch_flower()
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
                    print(f"Updated: {updated[2]} {updated[1]} now has {updated[4]} in stock")
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
                    confirm = input("This will permanently remove the bouquet, continue? (y/n) ").lower()
                    if confirm == "y":
                        flower_shop.delete_bouquet(bouquet_id)
                    else:
                        print("Discontinue aborted")
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
