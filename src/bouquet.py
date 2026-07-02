from flower import Flower

# Build the Bouquet class here


# This class is used to create flower bouquets.
# Each bouquet has a name and a dictionary
#   the dictionary determines which flowers and how many of each are needed to create this type of bouquet
class Bouquet:
    def __init__(self, name: str, flowers_and_quantity: dict):
        self.name = name
        self.flowers_and_quantity = flowers_and_quantity

#Test
