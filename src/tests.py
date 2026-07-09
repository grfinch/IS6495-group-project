import database_service as db

from flower import Flower
from bouquet import Bouquet

flower_shop = db.DatabaseService()

flower_shop.reset_database()

flower_shop.add_flower(Flower("Rose", "white", 1.49), 12)
flower_shop.add_flower(Flower("Rose", "Red", 1.49), 12)
print(f"fetch one flower: {flower_shop.fetch_flower(1)}")
print(f"fetch all flowers: {flower_shop.fetch_flower()}")

flower_shop.delete_flower(1)
flower_shop.add_flower(Flower("Rose", "Yellow", 1.49), 12)
print(f"fetch all flowers after modifications: {flower_shop.fetch_flower()}")

flower_shop.increase_stock(2, 20)
flower_shop.decrease_stock(3, 3)
print(f"fetch all flowers after stock updates: {flower_shop.fetch_flower()}")

flower_shop.add_bouquet(Bouquet("Red Rose bouquet", {2: 12}))
flower_shop.add_bouquet(Bouquet("Red/Yellow Rose bouquet", {2: 6, 3: 6}))
print(f"fetch one bouquet: {flower_shop.fetch_bouquet(1)}")
print(f"fetch all bouquets: {flower_shop.fetch_bouquet()}")

flower_shop.delete_bouquet(1)
print(f"fetch all bouquets after deletion: {flower_shop.fetch_bouquet()}")
