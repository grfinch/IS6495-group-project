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
class DatabaseService:
    def __init__(self):
        pass


# Required operations:
#   View inventory (RETRIEVE the data)
#   Add a new type of flower (CREATE a new flower entry in the database)
#   Buy more flowers (UPDATE existing flower count)
#   Create a new type of bouquet (CREATE a new bouquet entry in the database)
#   Assemble a bouquet (UPDATE: remove flowers from inventory to create a bouquet, then add the new bouquet to inventory)
#   Discontinue a type of bouquet (DELETE an existing bouquet type from inventory.  If there are more than zero of that bouquet, ask they user if they are sure)
#   Sell a bouquet (UPDATE the number of bouquets in inventory.  Track money?? I think money might be out of scope.  If we get done early, we can add it)
#   Do something with user management.  Customers and Employees? I haven't gotten that far yet.
