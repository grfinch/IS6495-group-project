from flower import Flower
from helper_functions import normalize_string


# This class is used to create flower bouquets.
# Each bouquet has a name and a dictionary
#   the dictionary determines which flower ids and how many of each are needed to create this type of bouquet
class Bouquet:

    SURCHARGE = 0.1  # 10%

    def __init__(self, name: str, flowers_and_quantity: dict[int, int]):
        self.name = normalize_string(name)
        self.flowers_and_quantity = flowers_and_quantity

    # These methods below need to be moved to the database_service class and updated to work there
    # Because the Bouquet class doesn't know about the database and can't directly access it.

    # def calculate_price(self) -> float:
    #     # returns price * quantity for each flower needed in this bouquet, then adds a markup
    #     total = 0.0
    #     for flower_id, quantity in self.flowers_and_quantity.items():
    #         flower =
    #         total += flower.price * quantity
    #     return total * (1 + self.SURCHARGE)

    # def can_be_made(self, flower_inventory: dict[int, int]) -> bool:
    #     # Checks whether there's enough stock of every flower needed
    #     for flower_id, quantity in self.flowers_and_quantity.items():
    #         flower = flower_inventory[
    #             flower_id
    #         ]  # use fetch_flower instead of passing the inventory as a parameter
    #         if flower.quantity_in_stock < quantity:
    #             return False
    #     return True

    # def build(self, flower_inventory: dict[int, int]):
    #     # Removes the needed quantity of each flower from stock
    #     # Should only be called after checking can_be_made()
    #     for flower_id, quantity in self.flowers_and_quantity.items():
    #         flower = flower_inventory[
    #             flower_id
    #         ]  # use fetch_flower instead of passing the inventory as a parameter
    #         flower.remove_stock(quantity)
