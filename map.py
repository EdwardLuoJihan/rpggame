c1 = 40
c2 = 0
from collections import deque

def calculate_depth(nodes, target_node):
    depth = 0
    current_node = target_node
    
    # Trace back the node path until reaching node 1
    while current_node != 1:
        # Find the node that connects to the current node
        for source_node, next_node, c in nodes:
            if next_node == current_node:
                # Move to the source node and increment depth
                current_node = source_node
                depth += 1
                break
    
    return depth  

def generate_html_tree(locations, nodes, current):

    # Dictionary to keep track of the Y positions of each location based on levels
    level_positions = {}
    
    # Create SVG element
    html = "<svg style='position: absolute; top: 0; left: 0; width: 100%; height: 100%;'>"
    
    # Populate level positions list
    max_level = max(len([n for n in nodes if n[0] == i]) for i in range(1, len(locations) + 1))

    i=0
    for location_id, location_data in locations.items():
        if location_data[1] == "V":
            if i == 0:
                x = 10.5 * c1 + c2
                i+=1
            else:
                x = location_id * c1 + c2
            y = 50 + (calculate_depth(nodes, location_id)) * 50  # Adjust Y elevation based on node depth
            level_positions[location_id] = (x, y)


    # Create lines between nodes
    for node in nodes:
        source_id, target_id, distance = node
        if locations[source_id][1] == "V" and locations[target_id][1] == "V":
            x1 = level_positions.get(source_id, (0, 0))[0]
            y1 = level_positions.get(source_id, (0, 0))[1]  # Use get() method to provide default value
            x2 = level_positions.get(target_id, (0, 0))[0] 
            y2 = level_positions.get(target_id, (0, 0))[1]  # Use get() method to provide default value
            html += f"<line class='line' id='{source_id}_{target_id}' x1='{x1}' y1='{y1}' x2='{x2}' y2='{y2}' style='stroke: {locations[target_id][2]}; stroke-width: 3px;'/>"
            if y1 > y2:
                xoffset = -7
            elif y2 > y1:
                xoffset = 7
            else:
                xoffset = 0
            yoffset = 0
            #html += f"<text x='{(x1 + x2) / 2 + xoffset}' font-size='17px' y='{(y1 + y2) / 2 + yoffset}' style='text-anchor: middle;fill:white;'>{distance}</text>"

    # Create nodes on top of lines
    
    i=0
    for location_id, location_data in locations.items():
        if location_data[1] == "V":
            if i == 0:
                x = 10.5 * c1 + c2
                i+=1
            else:
                x = location_id * c1 + c2
            y = 50 + (calculate_depth(nodes, location_id)) * 50  # Adjust Y elevation based on node depth
            if location_id == current:
                html += f"<circle class='node node{location_id}' cx='{x}' cy='{y}' r='25' stroke='white' fill='black' stroke-width='2px'/>"
            html += f"<circle class='node node{location_id}' cx='{x}' cy='{y}' r='20' fill='{location_data[2]}'/>"
            html += f"<text class='node node{location_id}' x='{x}' y='{y + 5}' font-size='20px' style='text-anchor: middle;fill:black;'>{location_id}</text>"
    
    
    html += "</svg>"
    
    return html