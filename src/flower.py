import helper_functions


# Represents a single type of flower available in the shop's inventory
class Flower:
    def __init__(
        self, name: str, color: str, price: float, reorder_threshold: int = 10
    ):
        self.name = helper_functions.normalize_string(name)
        self.color = helper_functions.normalize_string(color)
        self.price = price
