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
