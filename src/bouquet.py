from flower import Flower

# Build the Bouquet class here


# This class is used to create flower bouquets.
# Each bouquet has a name and a dictionary
#   the dictionary determines which flowers and how many of each are needed to create this type of bouquet
class Bouquet:
    def __init__(self, name: str, flowers_and_quantity: dict):
        self.name = name
        self.flowers_and_quantity = flowers_and_quantity

    def calculate_price(self, flower_inventory: dict) -> float:
        # Adds up price * quantity for each flower needed in this bouquet
        total = 0.0
        for flower_name, quantity in self.flowers_and_quantity.items():
            flower = flower_inventory[flower_name]
            total += flower.price * quantity
        return total

    def can_be_made(self, flower_inventory: dict) -> bool:
        # Checks whether there's enough stock of every flower needed
        for flower_name, quantity in self.flowers_and_quantity.items():
            flower = flower_inventory[flower_name]
            if flower.quantity_in_stock < quantity:
                return False
        return True

    def build(self, flower_inventory: dict):
        # Removes the needed quantity of each flower from stock
        # Should only be called after checking can_be_made()
        for flower_name, quantity in self.flowers_and_quantity.items():
            flower = flower_inventory[flower_name]
            flower.remove_stock(quantity)
