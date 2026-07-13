import sqlite3
import hashlib
import os

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
#   User management: Customer and Employee accounts (see methods below)
class DatabaseService(db.DBbase):

    def __init__(self):
        super().__init__("../flowershopDB.sqlite")

    def _hash_password(self, password: str, salt: str = None):
        # Returns (password_hash, salt). Generates a new random salt if one
        # isn't passed in (used when checking a password against a stored
        # hash, we reuse that account's existing salt).
        if salt is None:
            salt = os.urandom(16).hex()
        password_hash = hashlib.sha256((salt + password).encode()).hexdigest()
        return password_hash, salt

    
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

    ##### Gets the list of flowers needed to make one bouquet
    def fetch_bouquet_recipe(self, bouquet_id: int):
        # Returns the list of flowers and quantities needed for one bouquet.
        # Each row is (name, color, price, quantity, flower_id).
        # JOINs the recipe table to Flower so we get names, not just ids.
        # flower_id is included last so sell/price/stock checks can look
        # flowers back up without breaking the (name, color, price, qty)
        # order that the menu display code relies on.
        try:
            return self.cursor.execute(
                """SELECT f.name, f.color, f.price, bfq.quantity, f.flower_id
                   FROM Bouquet_Flower_Quantity bfq
                   JOIN Flower f ON bfq.flower_id = f.flower_id
                   WHERE bfq.bouquet_id = ?;""",
                (bouquet_id,),
            ).fetchall()
        except Exception as e:
            print("An error occurred while fetching the bouquet recipe: ", e)

    def delete_bouquet(self, bouquet_id: int):
        try:
            self.cursor.execute(
                "DELETE FROM Bouquet WHERE bouquet_id = ?", (bouquet_id,)
            )
            self.connection.commit()
            print(f"Deleted bouquet id {bouquet_id} successfully")
        except Exception as e:
            print("An error occurred while deleting the bouquet: ", e)

    def calculate_bouquet_price(self, bouquet_id: int) -> float:
        # price * quantity for each flower in the recipe, plus Bouquet's markup.
        # It lives here because it needs to look up current flower prices,
        # which the Bouquet class has no way to do.
        try:
            recipe = self.fetch_bouquet_recipe(bouquet_id)
            if not recipe:
                return 0.0
            total = sum(price * quantity for _, _, price, quantity, _ in recipe)
            return total * (1 + Bouquet.SURCHARGE)
        except Exception as e:
            print("An error occurred while calculating the bouquet price: ", e)

    def can_make_bouquet(self, bouquet_id: int) -> bool:
        # Checks whether there's enough of every flower in stock to make one
        # of this bouquet right now.
        try:
            recipe = self.fetch_bouquet_recipe(bouquet_id)
            if not recipe:
                return False
            for _, _, _, quantity_needed, flower_id in recipe:
                flower = self.fetch_flower(flower_id)
                if flower is None or flower[4] < quantity_needed:
                    return False
            return True
        except Exception as e:
            print("An error occurred while checking bouquet availability: ", e)
            return False

    def sell_bouquet(self, bouquet_id: int) -> bool:
        # Sells one of the given bouquet: pulls the flowers it needs out of inventory.
        # Calls can_make_bouquet() to be sure nothing gets partially decremented

        # Money tracking is intentionally left out for now (see the note in
        # the class docstring above) - this just handles the inventory side.
        try:
            if not self.can_make_bouquet(bouquet_id):
                print("Not enough flowers in stock to make this bouquet.")
                return False

            recipe = self.fetch_bouquet_recipe(bouquet_id)
            for _, _, _, quantity_needed, flower_id in recipe:
                self.decrease_stock(flower_id, quantity_needed)

            print("Sold 1 bouquet successfully")
            return True
        except Exception as e:
            print("An error occurred while selling the bouquet: ", e)
            return False


    
    #############################
    # Customer database methods #
    #############################
    def add_customer(self, username: str, password: str, name: str, email: str = None):
        # Creates a new customer account. Returns the account's public info
        # (never the password hash/salt) on success, or None if it failed -
        # most commonly because the username is already taken.
        try:
            password_hash, salt = self._hash_password(password)
            self.cursor.execute(
                "INSERT INTO Customer (username, password_hash, salt, name, email) VALUES (?, ?, ?, ?, ?);",
                (username, password_hash, salt, name, email),
            )
            self.connection.commit()
            customer_id = self.cursor.lastrowid
            print(f"Created customer account for {username}")
            return (customer_id, username, name, email)
        except sqlite3.IntegrityError:
            print("That username is already taken.")
            return None
        except Exception as e:
            print("An error occurred while creating the customer account: ", e)
            return None
 
    def fetch_customer(self, id: int = None):
        # Public info only - never returns password_hash/salt
        try:
            if id is not None:
                return self.cursor.execute(
                    "SELECT customer_id, username, name, email FROM Customer WHERE customer_id = ?",
                    (id,),
                ).fetchone()
            else:
                return self.cursor.execute(
                    "SELECT customer_id, username, name, email FROM Customer"
                ).fetchall()
        except Exception as e:
            print("An error occurred while fetching the customer(s): ", e)
 
    def fetch_customer_by_username(self, username: str):
        try:
            return self.cursor.execute(
                "SELECT customer_id, username, name, email FROM Customer WHERE username = ?",
                (username,),
            ).fetchone()
        except Exception as e:
            print("An error occurred while fetching the customer: ", e)
 
    def update_customer_email(self, customer_id: int, email: str):
        try:
            self.cursor.execute(
                "UPDATE Customer SET email = ? WHERE customer_id = ?", (email, customer_id)
            )
            self.connection.commit()
            print("Updated customer email successfully")
        except Exception as e:
            print("An error occurred while updating the customer: ", e)
 
    def delete_customer(self, customer_id: int):
        try:
            self.cursor.execute("DELETE FROM Customer WHERE customer_id = ?", (customer_id,))
            self.connection.commit()
            print(f"Deleted customer id {customer_id} successfully")
        except Exception as e:
            print("An error occurred while deleting the customer: ", e)
 
    def authenticate_customer(self, username: str, password: str):
        # Returns the customer's public info if the password matches, else None
        try:
            row = self.cursor.execute(
                "SELECT customer_id, username, password_hash, salt, name, email FROM Customer WHERE username = ?",
                (username,),
            ).fetchone()
            if row is None:
                return None
            customer_id, db_username, password_hash, salt, name, email = row
            check_hash, _ = self._hash_password(password, salt)
            if check_hash == password_hash:
                return (customer_id, db_username, name, email)
            return None
        except Exception as e:
            print("An error occurred while logging in: ", e)
            return None
 
    #############################
    # Employee database methods #
    #############################
    def add_employee(self, username: str, password: str, name: str):
        try:
            password_hash, salt = self._hash_password(password)
            self.cursor.execute(
                "INSERT INTO Employee (username, password_hash, salt, name) VALUES (?, ?, ?, ?);",
                (username, password_hash, salt, name),
            )
            self.connection.commit()
            employee_id = self.cursor.lastrowid
            print(f"Created employee account for {username}")
            return (employee_id, username, name)
        except sqlite3.IntegrityError:
            print("That username is already taken.")
            return None
        except Exception as e:
            print("An error occurred while creating the employee account: ", e)
            return None
 
    def fetch_employee(self, id: int = None):
        try:
            if id is not None:
                return self.cursor.execute(
                    "SELECT employee_id, username, name FROM Employee WHERE employee_id = ?",
                    (id,),
                ).fetchone()
            else:
                return self.cursor.execute(
                    "SELECT employee_id, username, name FROM Employee"
                ).fetchall()
        except Exception as e:
            print("An error occurred while fetching the employee(s): ", e)
 
    def fetch_employee_by_username(self, username: str):
        try:
            return self.cursor.execute(
                "SELECT employee_id, username, name FROM Employee WHERE username = ?",
                (username,),
            ).fetchone()
        except Exception as e:
            print("An error occurred while fetching the employee: ", e)
 
    def delete_employee(self, employee_id: int):
        try:
            self.cursor.execute("DELETE FROM Employee WHERE employee_id = ?", (employee_id,))
            self.connection.commit()
            print(f"Deleted employee id {employee_id} successfully")
        except Exception as e:
            print("An error occurred while deleting the employee: ", e)
 
    def authenticate_employee(self, username: str, password: str):
        try:
            row = self.cursor.execute(
                "SELECT employee_id, username, password_hash, salt, name FROM Employee WHERE username = ?",
                (username,),
            ).fetchone()
            if row is None:
                return None
            employee_id, db_username, password_hash, salt, name = row
            check_hash, _ = self._hash_password(password, salt)
            if check_hash == password_hash:
                return (employee_id, db_username, name)
            return None
        except Exception as e:
            print("An error occurred while logging in: ", e)
            return None

    ############################
    # General database methods #
    ############################
    def reset_database(self):
        # This database uses a many-to-many relationship.
        # That relationship is stored in the Bouquet_Flower_Quantity table.
        # Also creates the Customer and Employee account tables.
        try:
            sql = """
                DROP TABLE IF EXISTS Bouquet_Flower_Quantity;
                DROP TABLE IF EXISTS Bouquet;
                DROP TABLE IF EXISTS Flower;
                DROP TABLE IF EXISTS Customer;
                DROP TABLE IF EXISTS Employee;

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

                CREATE TABLE Customer (
                    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    name TEXT NOT NULL,
                    email TEXT
                );

                CREATE TABLE Employee (
                    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    name TEXT NOT NULL
                );
            """
            self.execute_script(sql)
        except Exception as e:
            print("An error occurred: ", e)