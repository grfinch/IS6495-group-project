from flower import Flower
from bouquet import Bouquet
import helper_functions
import db_base as db

# Build the database interactions here

"""
RUBRIC:

Full CRUD implementation: Create, Retrieve, Update and Delete functions for interaction with the database.
All tables are properly implemented
Must have at least 3 tables (entities)
Data are well populated (average of 20 rows total)
*Must not be static (need to interact with the DB)


NOTE: the rubric says that a DBbase class is provided, but I could't find one
"""


# This is used to access and update the database
# Required operations:
#   Add a new type of flower (CREATE a new flower entry in the database)
#   Fetch flowers (RETRIEVE the data for flowers)
#   Buy more flowers (UPDATE quantity)
#   Remove flowers from stock (UPDATE quantity)
#   Fetch bouquets (RETRIEVE the data for bouquets)
#   Create a new type of bouquet (CREATE a new bouquet entry in the database)
#   Discontinue a type of bouquet (DELETE an existing bouquet type from inventory.  If there are more than zero of that bouquet, ask they user if they are sure)
#   Sell a bouquet (UPDATE: remove flowers from inventory to create the bouquet. Track money?? I think money might be out of scope.  If we get done early, we can add it)
#   Do something with user management.  Customers and Employees? I haven't gotten that far yet.
class DatabaseService(db.DBbase):

    def __init__(self):
        super().__init__("../flowershopDB.sqlite")

    ###########################
    # Flower database methods #
    ###########################
    def add_flower(self, flower: Flower, quantity: int = 0):
        try:
            self.cursor.execute(
                "INSERT INTO Flower (name, color, price, quantity) VALUES(?, ?, ?, ?);",
                (flower.name, flower.color, flower.price, quantity),
            )
            self.connection.commit()
            print(f"Added {flower.color} {flower.name} successfully")
        except Exception as e:
            print("An error occurred while adding the flower: ", e)

    def delete_flower(self, flower_id: int):
        try:
            self.cursor.execute("DELETE FROM Flower WHERE flower_id = ?;", (flower_id,))
            self.connection.commit()
            print(f"Deleted flower id {flower_id} successfully")
        except Exception as e:
            print("An error occurred while deleting the flower: ", e)

    def fetch_flower(self, id: int = None):
        # if Id is null (None), then get all flowers, else get by id
        try:
            if id is not None:
                return self.cursor.execute(
                    "SELECT * FROM Flower WHERE flower_id = ?", (id,)
                ).fetchone()
            else:
                return self.cursor.execute("SELECT * FROM Flower").fetchall()
        # TODO: We should probably convert the record into a flower object when we retrieve it so it's easier to pass around and manipulate
        except Exception as e:
            print("An error occurred while fetching the flower(s): ", e)

    def needs_reorder(self, flower_id: int) -> bool:
        flower = self.fetch_flower(flower_id)
        print(f"This is the flower you got back: {flower}")
        # If quantity_remaining < reorder_threshold, return True
        # TODO: finish this method
        pass

    def _update_stock(self, flower_id: int, amount: int):
        try:
            self.cursor.execute(
                "UPDATE Flower SET quantity = quantity + ? WHERE flower_id = ?",
                (amount, flower_id),
            )
            self.connection.commit()
        except Exception as e:
            print("An error occurred while updating flower stock: ", e)

    def increase_stock(self, flower_id: int, amount: int):
        self._update_stock(flower_id, amount)

    def decrease_stock(self, flower_id: int, amount: int):
        self._update_stock(flower_id, -amount)

    ############################
    # Bouquet database methods #
    ############################
    def add_bouquet(self, bouquet: Bouquet):
        try:
            # Add the bouquet to the Bouquet table
            self.cursor.execute(
                "INSERT INTO Bouquet (name) VALUES(?);",
                (bouquet.name,),
            )
            # Add the flower and quantity mappings to the Bouquet_Flower_Quantity table
            bouquet_id = self.cursor.lastrowid
            for flower_id, quantity in bouquet.flowers_and_quantity.items():
                self.cursor.execute(
                    "INSERT INTO Bouquet_Flower_Quantity (bouquet_id, flower_id, quantity) VALUES(?, ?, ?);",
                    (bouquet_id, flower_id, quantity),
                )
            self.connection.commit()
            print(f"Added {bouquet.name} successfully")
        except Exception as e:
            print("An error occurred while adding the bouquet: ", e)

    def fetch_bouquet(self, id: int = None):
        # if Id is null (None), then get all bouquets, else get by id
        try:
            if id is not None:
                return self.cursor.execute(
                    "SELECT * FROM Bouquet WHERE bouquet_id = ?", (id,)
                ).fetchone()
            else:
                return self.cursor.execute("SELECT * FROM Bouquet").fetchall()

        except Exception as e:
            print("An error occurred while fetching the bouquet(s): ", e)

    def delete_bouquet(self, bouquet_id: int):
        try:
            self.cursor.execute(
                "DELETE FROM Bouquet WHERE bouquet_id = ?", (bouquet_id,)
            )
            self.connection.commit()
            print(f"Deleted bouquet id {bouquet_id} successfully")
        except Exception as e:
            print("An error occurred while deleting the bouquet: ", e)

    ############################
    # General database methods #
    ############################
    def reset_database(self):
        # This database uses a many-to-many relationship.
        # That relationship is stored in the Bouquet_Flower_Quantity table.
        try:
            sql = """
                DROP TABLE IF EXISTS Bouquet_Flower_Quantity;
                DROP TABLE IF EXISTS Bouquet;
                DROP TABLE IF EXISTS Flower;

                CREATE TABLE Flower (
                    flower_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    color TEXT NOT NULL,
                    price REAL NOT NULL CHECK (price >= 0),
                    quantity INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
                    UNIQUE (name, color)
                );

                CREATE TABLE Bouquet (
                    bouquet_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                );

                CREATE TABLE Bouquet_Flower_Quantity (
                    bouquet_id INTEGER NOT NULL,
                    flower_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL CHECK (quantity > 0),

                    PRIMARY KEY (bouquet_id, flower_id),

                    FOREIGN KEY (bouquet_id)
                        REFERENCES Bouquet(bouquet_id)
                        ON DELETE CASCADE
                        ON UPDATE CASCADE,

                    FOREIGN KEY (flower_id)
                        REFERENCES Flower(flower_id)
                        ON DELETE CASCADE
                        ON UPDATE CASCADE
                );
            """
            self.execute_script(sql)
        except Exception as e:
            print("An error occurred: ", e)
