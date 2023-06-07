# Import required libraries
import pandas as pd
import numpy as np
import graphviz
from datetime import datetime, timedelta

# Import required constants
from constants import ACTIVE_LINKS_PATH, ROADS_DETAILS_PATH, HELP_MESSAGE

# Function that generates the response based on user input
def handle_response(message):
    
    # Transform to Lower-Case
    lc_message = message.lower().split(" ")
    command = lc_message[0]

    # User wants to query a map's links
    if command == "!map":
        # Open the roads details database
        roads_db = pd.read_csv(ROADS_DETAILS_PATH)
        # Get relevant parameters
        curr_map = get_full_name(lc_message[1].lower()).lower()
        # Get the various details
        req_cols = ["Fiber", "Hide", "Ore", "Stone", "Wood", 
                    "Dungeon_Elite", "Dungeon_Group", "Dungeon_Solo",
                    "Roads_Group", "Roads_Raid", "Roads_Solo"]
        curr_row = roads_db.loc[roads_db['Name'] == curr_map, req_cols].values[0]
        # Return the message
        message = f"{curr_map} contains the following:\n\n"
        for i in range(len(req_cols)):
            feature = req_cols[i]
            is_present = False if np.isnan(curr_row[i]) else True
            if is_present:
                message += f"{feature}\n"
        return False, message

    # User wants to add a zone
    if command == "!add":
        # Open the current links file
        # Format - Current Zone, Neighbour Zone, Type, Closing Time
        links_db = pd.read_csv(ACTIVE_LINKS_PATH)
        # Open the roads details database
        roads_db = pd.read_csv(ROADS_DETAILS_PATH)
        # Get relevant parameters
        curr_map = get_full_name(lc_message[1].lower()).lower()
        new_map = get_full_name(lc_message[2].lower()).lower()
        portal_type = lc_message[3]
        hours_left, minutes_left = int(lc_message[4][:2]), int(lc_message[4][2:])
        # Check if zones are in the list of actual zones
        actual_zones = roads_db['Name'].values
        if curr_map not in actual_zones:
            return False, f"{curr_map} is not an actual zone!"
        if new_map not in actual_zones:
            return False, f"{new_map} is not an actual zone!"
        # Calculate Closing Time
        now = datetime.now()
        closing_time = now + timedelta(hours=hours_left, minutes=minutes_left)
        closing_time_str = str(closing_time.strftime("%d/%m/%Y %H:%M"))
        # Add the link to the Active Links Database
        links_db.loc[len(links_db)] = [curr_map, new_map, portal_type, closing_time_str]
        links_db.loc[len(links_db)] = [new_map, curr_map, portal_type, closing_time_str]
        # Export updated DB
        links_db.to_csv(ACTIVE_LINKS_PATH, index=False)
        # Return success message
        return False, f"Added {new_map} to {curr_map} until {closing_time_str}!"

    # User wants to delete a zone
    if command == "!delete":
        # Read the roads link database
        links_db = pd.read_csv(ACTIVE_LINKS_PATH)
        # Open the roads details database
        roads_db = pd.read_csv(ROADS_DETAILS_PATH)
        # Get the full names of the zones
        zone_1 = get_full_name(lc_message[1].lower()).lower()
        zone_2 = get_full_name(lc_message[2].lower()).lower()
        # Check if zones are in the list of actual zones
        actual_zones = roads_db['Name'].values
        if zone_1 not in actual_zones:
            return False, f"{zone_1} is not an actual zone!"
        if zone_2 not in actual_zones:
            return False, f"{zone_2} is not an actual zone!"
        # Remove the link in the database
        links_db = links_db.drop(links_db[(links_db['Current Zone'] == zone_1) & (links_db['Neighbour Zone'] == zone_2)].index)
        links_db = links_db.drop(links_db[(links_db['Current Zone'] == zone_2) & (links_db['Neighbour Zone'] == zone_1)].index)
        # Export updated DB
        links_db.to_csv(ACTIVE_LINKS_PATH, index=False)
        # Return success message
        return False, f"Deleted link between {zone_2} and {zone_1}!"

    # User wants to check a zone's layout
    if command == "!show":
        # Read the roads link database
        links_db = pd.read_csv(ACTIVE_LINKS_PATH)
        # Open the roads details database
        roads_db = pd.read_csv(ROADS_DETAILS_PATH)
        # Get relevant parameters
        queried_map = get_full_name(lc_message[1].lower()).lower()
        # Instantiate the node list with the queried zone
        visited_nodes = []
        node_list = [queried_map]
        # Instantiate a list for edges
        edge_list = []
        # Instantiate the graph
        G = graphviz.Digraph()
        # Get all the links in a recursive manner
        while node_list:
            # Get the first node
            curr_node = node_list.pop(0)
            # Get all the neighbouring nodes to the current node if the current node has yet been visited
            if curr_node not in visited_nodes:
                # Add the current node into the graph
                node_row = list(roads_db[['Name', 'Tier', 'Type']][roads_db['Name'] == curr_node].values[0])
                node_name, node_tier, node_type = node_row
                node_str = node_name + "\n" + "T" + str(node_tier) + " " + node_type
                G.node(node_name, style='filled', color="pink", shape="box", label=node_str)
                # Add the neighbouring nodes
                visited_nodes.append(curr_node)
                neighbouring_nodes = list(links_db.loc[links_db['Current Zone'] == curr_node, "Neighbour Zone"].values)
                for neighbour in neighbouring_nodes:
                    if neighbour not in visited_nodes:
                        portal_type, closing_time = links_db.loc[(links_db['Current Zone'] == curr_node) & (links_db['Neighbour Zone'] == neighbour), ["Type", "Closing Time"]].values[0]
                        node_list.append(neighbour)
                        edge_list.append((curr_node, neighbour, portal_type, closing_time))
        # Add the various edges
        for edge in edge_list:
            # Get the relevant node information
            source_node, dest_node, portal_type, closing_time = edge
            # Calculate time left
            closing_dt = datetime.strptime(closing_time, "%d/%m/%Y %H:%M")
            time_difference_in_minutes = (closing_dt - datetime.now()).seconds / 60
            hours_left = int(time_difference_in_minutes // 60)
            minutes_left = int(time_difference_in_minutes % 60)
            G.edge(source_node, dest_node, label=f"{portal_type.upper()} {closing_time}\n{hours_left}H{minutes_left}M")
        # Save the graph before sending it in the channel
        filename = "Temp"
        G.render(filename, format="png")
        return True, filename + ".png"

    # Help command
    if command == "!help":
        return False, HELP_MESSAGE

# Function to get full name if short form is given
def get_full_name(given_name):
    # Get the roads database
    roads_db = pd.read_csv(ROADS_DETAILS_PATH)
    # Check if short form is used
    if len(given_name) == 6:
        full_name = roads_db.loc[roads_db['Short Form'] == given_name, "Name"].values[0]
        return full_name
    else:
        return given_name