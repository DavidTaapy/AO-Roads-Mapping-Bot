# Import required libraries
import pandas as pd
import numpy as np
import graphviz
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# Import required constants
from constants import ACTIVE_LINKS_PATH, ROADS_DETAILS_PATH, ROYALS_DETAILS_PATH, WORLD_XML_PATH, RESOURCE_TYPES_PATH
from constants import HELP_MESSAGE, COLOR_DICT
from constants import RESOURCE_LAYERS, AVA_CHEST_LAYERS, DUNGEON_LAYERS

# Function that generates the response based on user input
def handle_response(message):
    
    # Open the active links file
    links_db = pd.read_csv(ACTIVE_LINKS_PATH)
    # Open the roads details database
    roads_db = pd.read_csv(ROADS_DETAILS_PATH)
    # Open the royals details database
    royals_db = pd.read_csv(ROYALS_DETAILS_PATH)
    # Open the resource types database
    resources_db = pd.read_csv(RESOURCE_TYPES_PATH)
    # Open the world xml file
    world_xml = open_xml(WORLD_XML_PATH)
    # Transform to Lower-Case and split the given user input
    lc_message = message.lower().split(" ")
    command = lc_message[0]

    # User wants to query a map's links
    if command == "!show":
        # Get relevant parameters
        curr_map = get_full_name(lc_message[1]).title()
        # Instantiate the message
        message = f"**{curr_map}** contains the following:\n\n"
        # Open the XML file for the given map
        cluster = find_cluster(world_xml, curr_map) 
        file_id = cluster['file']
        cluster_xml = open_xml(f"./Data/Roads Game Files/Cluster/cluster/{file_id}")
        message = add_features_for_zone(cluster_xml, resources_db, message)
        # Return message
        return False, message

    # User wants to add a zone
    if command == "!add":
        # Get relevant parameters
        curr_map = get_full_name(lc_message[1])
        new_map = get_full_name(lc_message[2])
        portal_type = lc_message[3]
        duration = lc_message[4]
        # Get the hours and minutes based of the two formats - HH:MM / HHMM
        if ":" in duration:
            hours_left, minutes_left = duration.split(":")
        else:
            hours_left, minutes_left = duration[:2], duration[2:]
        hours_left = int(hours_left)
        minutes_left = int(minutes_left)
        # Check if zones are in the list of actual zones
        roads_zones = roads_db['Name'].values
        royal_zones = royals_db['Zone'].values
        if (curr_map not in roads_zones) and (curr_map not in royal_zones):
            return False, f"{curr_map} is not an actual zone!"
        if (new_map not in roads_zones) and (new_map not in royal_zones):
            return False, f"{new_map} is not an actual zone!"
        # Calculate Closing Time
        now = datetime.now()
        closing_time = now + timedelta(hours=hours_left, minutes=minutes_left)
        closing_time_str = str(closing_time.strftime("%d/%m/%Y %H:%M"))
        # Add the links to the Active Links Database - Both ways
        links_db.loc[len(links_db)] = [curr_map, new_map, portal_type, closing_time_str]
        links_db.loc[len(links_db)] = [new_map, curr_map, portal_type, closing_time_str]
        # Export updated DB
        links_db.to_csv(ACTIVE_LINKS_PATH, index=False)
        # Return success message
        return False, f"Added {new_map} to {curr_map} until {closing_time_str}!"

    # User wants to delete a zone
    if command == "!delete":
        # Get the full names of the zones
        zone_1 = get_full_name(lc_message[1])
        zone_2 = get_full_name(lc_message[2])
        # Check if zones are in the list of actual zones
        roads_zones = roads_db['Name'].values
        royal_zones = royals_db['Zone'].values
        if (zone_1 not in roads_zones) and (zone_1 not in royal_zones):
            return False, f"{curr_map} is not an actual zone!"
        if (zone_2 not in roads_zones) and (zone_2 not in royal_zones):
            return False, f"{new_map} is not an actual zone!"
        # Remove the link in the database
        links_db = links_db.drop(links_db[(links_db['Current Zone'] == zone_1) & (links_db['Neighbour Zone'] == zone_2)].index)
        links_db = links_db.drop(links_db[(links_db['Current Zone'] == zone_2) & (links_db['Neighbour Zone'] == zone_1)].index)
        # Export updated DB
        links_db.to_csv(ACTIVE_LINKS_PATH, index=False)
        # Return success message
        return False, f"Deleted link between {zone_2} and {zone_1}!"

    # User wants to check a zone's layout
    if command == "!map":
        # Get relevant parameters
        queried_map = get_full_name(lc_message[1])
        # Instantiate the node list with the queried zone
        node_list = [queried_map]
        visited_list = []
        added_list = []
        # Instantiate the graph
        G = graphviz.Digraph()
        # Get all the links in a recursive manner
        while node_list:
            # Get the first node in the queue
            curr_node = node_list.pop(0)
            visited_list.append(curr_node)
            # Add the current node into the graph
            add_node_to_graph(curr_node, roads_db, royals_db, G)
            added_list.append(curr_node)
            # Add the neighbouring nodes
            neighbouring_nodes = list(links_db.loc[links_db['Current Zone'] == curr_node, "Neighbour Zone"].values)
            for neighbour in neighbouring_nodes:
                if neighbour not in visited_list:
                    # Get the relveant information
                    portal_type, closing_time = links_db.loc[(links_db['Current Zone'] == curr_node) & (links_db['Neighbour Zone'] == neighbour), ["Type", "Closing Time"]].values[0]
                    closing_dt = datetime.strptime(closing_time, "%d/%m/%Y %H:%M")
                    # Check if link has expired and remove if it has
                    if closing_dt < datetime.now():
                        # Remove the link in the database
                        links_db = links_db.drop(links_db[(links_db['Current Zone'] == curr_node) & (links_db['Neighbour Zone'] == neighbour)].index)
                        links_db = links_db.drop(links_db[(links_db['Current Zone'] == neighbour) & (links_db['Neighbour Zone'] == curr_node)].index)
                        # Export updated DB and re-import
                        links_db.to_csv(ACTIVE_LINKS_PATH, index=False)
                        continue
                    # Add neighbour to the queue
                    if neighbour not in visited_list:
                        node_list.append(neighbour)
                    # Calculate time left
                    added_list = add_edge_to_graph(curr_node, neighbour, portal_type, closing_dt, added_list, roads_db, royals_db, G)
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
    # Change to lower case
    given_name = given_name.lower()
    # Check if short form is used
    if len(given_name) == 6:
        full_name = roads_db.loc[roads_db['Short Form'] == given_name, "Name"].values[0]
        return full_name
    else:
        return given_name
    
# Function to get the information of a given node
def add_node_to_graph(curr_node, roads_db, royals_db, G):
    # Get the various list of zones in roads and royals respectively
    roads_zones = roads_db['Name'].values
    # Add the node if it is a roads zone
    if curr_node in roads_zones:
        node_name, node_tier, node_type = list(roads_db[['Name', 'Tier', 'Type']][roads_db['Name'] == curr_node].values[0])
        node_str = node_name + "\n" + "T" + str(node_tier) + " " + node_type
        G.node(node_name, style='filled', color="pink", shape="box", label=node_str)
    # Add the node as a royal zone
    else:
        node_name, node_type = list(royals_db[['Zone', 'Type']][royals_db['Zone'] == curr_node].values[0])
        node_str = node_name + "\n" + node_type + " zone"
        G.node(node_name, style='filled', color=COLOR_DICT[node_type], shape="box", label=node_str)

# Function to add edge to the graph
def add_edge_to_graph(source_node, dest_node, portal_type, closing_dt, added_list, roads_db, royals_db, G):
    # Add the duration node between the two zones
    time_difference_in_minutes = (closing_dt - datetime.now()).seconds / 60
    hours_left = int(time_difference_in_minutes // 60)
    minutes_left = int(time_difference_in_minutes % 60)
    middle_node_name = f"{source_node}-{dest_node}"
    node_str = f"{portal_type.upper()} {closing_dt}H\n{hours_left}H {minutes_left}M"
    G.node(middle_node_name, style="filled", color=COLOR_DICT[portal_type], shape="ellipse", label=node_str)
    G.edge(source_node, middle_node_name)
    # Add the neighbour zone
    if dest_node not in added_list:
        add_node_to_graph(dest_node, roads_db, royals_db, G)
        G.edge(middle_node_name, dest_node)
        added_list.append(dest_node)
    return added_list

# Function to open XML file
def open_xml(path):
    # Read the file data
    with open(path, 'r') as f:
        data = f.read()
    # Parse the file using BS4
    bs_data = BeautifulSoup(data, "xml")
    # Find all the clusters
    return bs_data

# Find the cluster given a cluster name
def find_cluster(xml_data, cluster_name):
    # Find all the clusters
    clusters = xml_data.findAll('cluster')
    # Find the given cluster's xml data
    for cluster in clusters:
        if cluster['displayname'] == cluster_name:
            return cluster
        
# Function to add features to a zone
def add_features_for_zone(cluster_xml, resources_db, message):
    # Add the resources in the zone
    message += add_resources_for_zone(cluster_xml, resources_db, RESOURCE_LAYERS, "resources")
    # Add the avalonian chests in the zone
    message += add_resources_for_zone(cluster_xml, resources_db, AVA_CHEST_LAYERS, "ava chests")
    # Add the dungeons in the zone
    message += add_resources_for_zone(cluster_xml, resources_db, DUNGEON_LAYERS, "dungeons")  
    return message

# # Function to add resources to a zone
def add_resources_for_zone(cluster_xml, features_db, feature_layer, feature_name):
    # Add the header message
    feature_list = []
    # Find all template instances
    template_instances = cluster_xml.findAll('templateinstance')
    # Find all the resource template instances
    for instance in template_instances:
        instance_ref = instance['ref']
        if instance_ref in feature_layer:
            active_layers = instance.findAll('activelayer')
            for layer in active_layers:
                layer_id = layer['id']
                # Add the layer if it is something we are interested in, else skip
                try:
                    feature_list.append(features_db.loc[(features_db['Name'] == instance_ref) & (features_db['Layer'] == layer_id), "Item"].values[0])
                except:
                    pass
    # Return the message
    message = ""
    if len(feature_list) > 0:
        message += f"The following {feature_name} are present:\n"
        for feature in feature_list:
            message += f"{feature}\n"
    return message + "\n"