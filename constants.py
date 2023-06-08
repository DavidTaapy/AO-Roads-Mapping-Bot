# File Paths
ROADS_DETAILS_PATH = "./Data/Roads_Details.csv"
ROYALS_DETAILS_PATH = "./Data/Royals_Details.csv"
UPDATE_LIST_PATH = "./Data/Update_List.csv"
ACTIVE_LINKS_PATH = "./Data/Active_Links.csv"

# Help Message
HELP_MESSAGE = """
Welcome to the Copycat Version of Breck's friend's Bot!  

This bot provides functions to record and display information on zones and portals found in Albion Online.  

All zone information has been extracted from the game files and all portal  
information is provided by players like you! If you're wondering why you can't  
see what zones are connected, it's because you haven't scouted it yet.  

Available commands:  

!help - Displays this help message in English.  
!add <zone 1> <zone 2> <color> <time> - Adds a portal between two zones.  
!map <zone> - Prints a map of all portals connected to this zone.  
!show <zone> - Shows all information for this zone.  
!delete <zone 1> <zone 2> - Deletes a portal between two zones.  

In these commands:  

<zone> is the name of a zone. You need correct spelling and punctuation!  
<color> indicates the color of the portal, which must be green (2-player), blue (7-player) or yellow (20-player).  
You can also use g, b, and y as shorthand!  
<time> is the remaining time left on the portal, which must be formatted as HHMM!  
"""