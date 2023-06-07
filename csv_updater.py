# The following script helps with updating the roads database using https://albionroamapp.com/search

# Import required libraries
import pandas as pd

# Import required information
from constants import ROADS_DETAILS_PATH, UPDATE_LIST_PATH

# Function that helps with updating the roads database
def update_roads_db(db_path, update_list_path, column_to_update, new_value):
    # Read the current roads database and list of zones to update
    db = pd.read_csv(db_path)
    update_list = pd.read_csv(update_list_path)
    # Update each zone in the update list for a specific column and the corresponding value
    for curr_zone in update_list['Update List']:
        db.loc[db['Name'] == curr_zone, column_to_update] = new_value
    # Replace the database with the updated version
    db.to_csv(db_path, index=False)

# Run the program
if __name__ == "__main__":
    # Specify the required paths
    db_path = ROADS_DETAILS_PATH
    update_list_path = UPDATE_LIST_PATH
    # Specify the required parameters
    column_to_update = 'Roads_Group'
    new_value = 1
    # Execute the function
    update_roads_db(db_path, update_list_path, column_to_update, new_value)