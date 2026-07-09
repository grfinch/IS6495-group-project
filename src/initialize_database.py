import csv
import database_service as db

from flower import Flower
from bouquet import Bouquet

flower_shop = db.DatabaseService()
flower_shop.reset_database()

with open("../data/Flower.csv", "r") as flower_csv:
    flower_reader = csv.DictReader(flower_csv)
    for row in flower_reader:
        flower = Flower(row["name"], row["color"], float(row["price"]))
        quantity = int(row["quantity"])
        flower_shop.add_flower(flower, quantity)

with open("../data/Bouquets_With_Recipes.csv", "r") as bouquet_csv:
    bouquet_reader = csv.DictReader(bouquet_csv)
    for row in bouquet_reader:
        name = row["name"]
        flowers_and_quantity = eval(row["flowers_and_quantity"])
        bouquet = Bouquet(name, flowers_and_quantity)
        flower_shop.add_bouquet(bouquet)
