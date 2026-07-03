# Build the Flower class here

class Flower:
    # Represents a single type of flower available in the shop's inventory
    def __init__(self, name: str, color: str, price: float, quantity_in_stock: int, reorder_threshold: int = 10):
        self.name = name
        self.color = color
        self.price = price
        self.quantity_in_stock = quantity_in_stock
        self.reorder_threshold = reorder_threshold

    def needs_reorder(self) -> bool:
         # Checks if stock has dropped to or below the reorder threshold
        return self.quantity_in_stock <= self.reorder_threshold

    def remove_stock(self, amount: int):
        # Removes flowers from stock
        if amount > self.quantity_in_stock:
            raise ValueError(f"Not enough {self.name} in stock.")
        self.quantity_in_stock -= amount

    def add_stock(self, amount: int):
         # Adds flowers to stock
        self.quantity_in_stock += amount