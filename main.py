from flask import *
import random
from map import generate_html_tree

app = Flask(__name__)

current_location = 1

level_scaling_rate = 2
level = 100
endurance_scaling_rate = 5
player_stats = {
    "strength": 10+level*10,
    "endurance": 10+level*10, #calculate stamina required
    "mana": 10+level*10,
    "agility": 10+level*10, #calculate stamina required
}
mana = 100 + player_stats["mana"] * level_scaling_rate
stamina = 100 + player_stats["endurance"] * endurance_scaling_rate
maxmana = 100 + player_stats["mana"] * level_scaling_rate
maxstamina = 100 + player_stats["endurance"] * endurance_scaling_rate
xp = 0
strength_factor = 8
base_xp = 100
scaling_factor = 10
xp_required = base_xp + (level ** 2 * scaling_factor)
hp = 100 + (player_stats["endurance"]*endurance_scaling_rate) + (level*level_scaling_rate) + (player_stats["strength"] * strength_factor)
hpmax = 100 + (player_stats["endurance"]*endurance_scaling_rate) + (level*level_scaling_rate) + (player_stats["strength"] * strength_factor)


### USER INTERACTIONS ###


def moveCost(d):
    global player_stats
    e = player_stats["endurance"]
    a = player_stats["agility"]

    return 100 * (d/(a+e))

def find_distance(a, b):
    for i in nodes:
        if i[0] == a or i[1] == a:
            if i[0] == b or i[1] == b:
                return i[2]
    return -1

locations = {
    1: ["Starter Town", "V", "#B28719"], #city name, visited status, and color
    2: ["City of Gears", "U", "#707b90"], 
    3: ["Floral Elevator", "U", "#8982c8"], 
    4: ["City of Ice", "U", "#c5eae7"], 
    5: ["Lily-pad Laketown", "U", "#e7fae1"], 
    6: ["City of Lightning", "U", "#0d22dd"], 
    7: ["The Cave of Lights", "U", "#F8FF14"] , 
    8: ["City of Masks", "U", "#fbba00"], 
    9: ["Abandoned Ghost Town", "U" , "#607a90"], 
    10: ["The Red City", "U", "#ff4f4f"],
    11: ["City of Gold", "U", "#FFD700"],
    12: ['City of Love', "U", "#FF9090"],
    13: ["City of Swans", "U", "#00FFEC"],
    14: ["Eternal Dawn", "U", "#FF9349"],
    15: ["The Lonely City", "U", "#D8D8D8"],
    16: ["Mystic Falls", "U", "#5426b2"],
    17: ["Sunflower Springs", "U", "#FFD700"],
    18: ["Silver Shores", "U", "#C0C0C0"],
    19: ["Whispering Pines", "U", "#228B22"],
    20: ["Phoenix Heights", "U", "#FF2400"]
}

nodes = [
    [1,2,6], #node 1, node 2, distance between them
    [1,4,5],
    [1,6,2],
    [1,8,3],
    [2,3,4],
    [4,5,5],
    [6,7,7],
    [8,9,9],
    [9,10,7],
    [9,11,3],
    [1,12,5],
    [7,13,2],
    [13,14,5],
    [12,15,7],
    [3,16,9],
    [5,17,11],
    [7,18,6],
    [18,14,5],
    [15,19,10],
    [11,15,8],
    [14,20,4],
    [19,20,15]
]

descriptions = {
    1: "A quaint town nestled at the foot of the mountains, where every journey begins.",
    2: "A bustling metropolis fueled by the ingenuity of its inhabitants and the gears that power it.",
    3: "A place where vibrant flowers bloom year-round, filling the air with their sweet scent.",
    4: "A city encased in ice, where the cold never thaws and mysteries lie frozen beneath its surface.",
    5: "A serene town built upon lily-pad covered waters, offering tranquility amidst nature's beauty.",
    6: "A city crackling with energy, where lightning dances across the sky and powers the machines of innovation.",
    7: "An underground marvel adorned with glowing lights, housing secrets and wonders waiting to be discovered.",
    8: "A city veiled in mystery and intrigue, where masks conceal both identity and purpose.",
    9: "A ghostly town abandoned by its inhabitants, shrouded in tales of hauntings and forgotten memories.",
    10: "A city of vibrant red hues, where passion and determination fuel every endeavor.",
    11: "A city adorned with golden splendor, where riches and prosperity abound for those who seek it.",
    12: "A city where love is in the air, its streets filled with romance and heartfelt connections.",
    13: "A city surrounded by swan-filled lakes, embodying grace, elegance, and beauty.",
    14: "A city where dawn lasts forever, bathing its streets in perpetual light and hope.",
    15: "A city of solitude, where quiet contemplation and introspection reign supreme.",
    16: "A mysterious town enveloped in an aura of magic and mysticism, where secrets linger in the air.",
    17: "A charming city known for its vast sunflower fields, radiating warmth and joy to all who visit.",
    18: "A coastal paradise with shimmering silver shores, where the sea meets the sky in a breathtaking display.",
    19: "A tranquil retreat nestled among whispering pine trees, offering solace and peace to weary souls.",
    20: "A city rising from the ashes with fiery determination, symbolizing resilience and rebirth."
}


def find_neighbors(x): #takes in variable for reference
    neighbors = []
    for node in nodes:
        if node[0] == x or node[1] == x:
            neighbors.append(locations[[i for i in node if i != x][0]][0])
    return neighbors

def find_neighborsindex(x): #takes in variable for reference
    neighbors = []
    for node in nodes:
        if node[0] == x or node[1] == x:
            neighbors.append([i for i in node if i != x][0])
    return neighbors

@app.route('/')
def index():
    return render_template("index.html", name='bob', race='human', option_stats={
        "mana": [mana, maxmana],
        "stamina": [stamina, maxstamina]
    }, level=level, xp=xp, xpmax=xp_required, hp=hp, hpmax=hpmax)

@app.route('/find_neighbors', methods=['GET'])
def return_neighbors():
    neighbors = find_neighbors(current_location)
    neighborsindex = find_neighborsindex(current_location)
    form = ""
    for n, i in enumerate(neighbors):
        costToMove = moveCost(find_distance(current_location, neighborsindex[n]))
        if costToMove > stamina:
            disable = True
        else:
            disable = False
        form += f"""<button class="locbutton disable-{disable}" id="{i}" onclick='moveto("{i}")'>{neighborsindex[n]} - {i}</button>"""
    return form

@app.route('/location', methods=['GET'])
def return_location():
    return f"<span style='color: {locations[current_location][2]}'>{locations[current_location][0]}</span>"

@app.route('/getstats', methods=['GET'])
def getstats():
    return list(map(int, [hp, mana, stamina, xp, xp_required]))

@app.route('/getmap', methods=['GET'])
def getmap():
    m = generate_html_tree(locations, nodes, current_location)
    return m

@app.route('/dsc', methods=['GET'])
def getdsc():
    n = request.args.get("n")
    return descriptions[int(n)]

@app.route('/fd', methods=['GET'])
def getl():
    s = request.args.get("s")
    t = request.args.get("t")
    if s == "CURRENT":
        s = current_location
    print(f"{str(find_distance(int(s), int(t)))}KM")
    return f"{str(find_distance(int(s), int(t)))}KM"

@app.route('/moveto', methods=['GET'])
def move_to():
    global current_location
    global stamina
    global hp
    global mana
    newlocation = request.args.get("loc")
    for i in locations:
        if newlocation in locations[i]:
            for n in nodes:
                if n[0] == i or n[1] == i:
                    if n[0] == current_location or n[1] == current_location:
                        distance = n[2]
                        cost = moveCost(distance)
                        print(stamina, cost)
                        if stamina >= cost:
                            current_location = i
                            locations[i][1] = "V"
                            stamina -= cost
                            return str(current_location)
                        else:
                            return "no bueno"
    return "no bueno"

# @app.route('/validateCost', methods=['GET'])
# def validateCost():
#     loc = request.args.get("loc")
#     for i in locations:
#         if loc in locations[i]:
#             for n in nodes:
#                 if n[0] == i or n[1] == i:
#                     if n[0] == current_location or n[1] == current_location:
#                         distance = n[2]
#                         cost = moveCost(distance)
#                         if stamina >= cost:
#                             return "bueno"
#                         else:
#                             return "no bueno"
#     return "no bueno"

if __name__ == "__main__":
    app.jinja_env.cache = {}
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='0.0.0.0', port=80)
