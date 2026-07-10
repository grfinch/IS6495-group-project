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
                        "exit": "Exit program"
                        }

    
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
                # pads the key to 8 characters so the menu lines up
                print(f"  [{key:<8}] {value}")
            print("-" * 40)

            user_selection = input("Enter an option: ").lower()

            # Create the database service to handle all DB interactions
            flower_shop = DatabaseService()

            if user_selection == "flowers":
                results = flower_shop.fetch_flower()
                for item in results:
                    print(f"  {item[2]} {item[1]} - ${item[3]:.2f}")
                   
                   
            elif user_selection == "bouquets":
                # Show every bouquet and the flowers inside it
                bouquets = flower_shop.fetch_bouquet()
                for bouquet in bouquets:
                    print(f"\n  {bouquet[1]}:")   # bouquet name
                    recipe = flower_shop.fetch_bouquet_recipe(bouquet[0])
                    for ingredient in recipe:
                        print(f"      {ingredient[3]} x {ingredient[1]} {ingredient[0]} (${ingredient[2]:.2f} each)")
                

            elif user_selection == "create":
                print("Placeholder: create a bouquet")


            elif user_selection == "order":
                print("Placeholder: order more flowers")

            else:
                # Only show the error if the input wasn't "exit"
                if user_selection != "exit":
                    print("Invalid selection, please try again.")

        print("\nThanks for visiting the Flower Shop! 🌸")


project = Project()
project.run()