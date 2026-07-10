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

class Project:

    def run(self):

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
        #                  buy a bouquet (this one isn't built yet - overlaps
        #                  with Gaven's "sell a bouquet" TODO in database_service)
        #
        # One idea: ask the role once at startup, then show a different
        # menu_options dictionary per role. But if you have a better approach,
        # go for it!
        #

    
        # Welcome banner 
      
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