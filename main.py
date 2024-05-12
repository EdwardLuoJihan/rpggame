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
    1: ["Starter Town", "V", "#B28719"], # city name, visited status, and color
    2: ["Eldergrove", "V", "#3CB371"],
    3: ["Crystal Peaks", "V", "#ADD8E6"],
    4: ["Dragon's Hollow", "V", "#8B0000"],
    5: ["Frostwind Citadel", "V", "#FFFFFF"],
    6: ["Whispering Woods", "V", "#228B22"],
    7: ["Mystic Falls", "V", "#4169E1"],
    8: ["Sunset Harbor", "V", "#FF4500"],
    9: ["Ancient Ruins of Zephyr", "V", "#DAA520"],
    10: ["Shadowvale Village", "V", "#4B0082"],
    11: ["Grimreach Caverns", "V", "#A0522D"],
    12: ["Celestial City", "V", "#FFFF00"],
    13: ["Thundering Steppes", "V", "#708090"],
    14: ["Sands of Time Desert", "V", "#F5DEB3"],
    15: ["Serpent's Spine", "V", "#8A2BE2"],
    16: ["Abyssal Depths", "V", "#000080"],
    17: ["Stormwatch Keep", "V", "#00CED1"],
    18: ["Emberwood Grove", "V", "#8B4513"],
    19: ["Shrouded Peaks", "V", "#778899"],
    20: ["Lost City of Atlantis", "V", "#00FFFF"]
}

nodes = [
    [1, 2, 5], # Starter Town to Eldergrove, distance: 5 days
    [1, 3, 8], # Starter Town to Crystal Peaks, distance: 8 days
    [1, 4, 10], # Starter Town to Dragon's Hollow, distance: 10 days
    [2, 5, 4], # Eldergrove to Frostwind Citadel, distance: 4 days
    [2, 6, 3], # Eldergrove to Whispering Woods, distance: 3 days
    [3, 7, 6], # Crystal Peaks to Mystic Falls, distance: 6 days
    [3, 8, 7], # Crystal Peaks to Sunset Harbor, distance: 7 days
    [4, 9, 12], # Dragon's Hollow to Ancient Ruins of Zephyr, distance: 12 days
    [5, 10, 9], # Frostwind Citadel to Shadowvale Village, distance: 9 days
    [5, 11, 5], # Frostwind Citadel to Grimreach Caverns, distance: 5 days
    [6, 12, 8], # Whispering Woods to Celestial City, distance: 8 days
    [6, 13, 6], # Whispering Woods to Thundering Steppes, distance: 6 days
    [7, 14, 10], # Mystic Falls to Sands of Time Desert, distance: 10 days
    [7, 15, 7], # Mystic Falls to Serpent's Spine, distance: 7 days
    [8, 16, 12], # Sunset Harbor to Abyssal Depths, distance: 12 days
    [8, 17, 9], # Sunset Harbor to Stormwatch Keep, distance: 9 days
    [9, 18, 5], # Ancient Ruins of Zephyr to Emberwood Grove, distance: 5 days
    [9, 19, 8], # Ancient Ruins of Zephyr to Shrouded Peaks, distance: 8 days
    [10, 20, 15], # Shadowvale Village to Lost City of Atlantis, distance: 15 days
    [11, 20, 13], # Grimreach Caverns to Lost City of Atlantis, distance: 13 days
    [12, 20, 11], # Celestial City to Lost City of Atlantis, distance: 11 days
    [13, 20, 12], # Thundering Steppes to Lost City of Atlantis, distance: 12 days
    [14, 20, 14], # Sands of Time Desert to Lost City of Atlantis, distance: 14 days
    [15, 20, 9], # Serpent's Spine to Lost City of Atlantis, distance: 9 days
    [16, 20, 16], # Abyssal Depths to Lost City of Atlantis, distance: 16 days
    [17, 20, 10], # Stormwatch Keep to Lost City of Atlantis, distance: 10 days
    [18, 20, 7], # Emberwood Grove to Lost City of Atlantis, distance: 7 days
    [19, 20, 6], # Shrouded Peaks to Lost City of Atlantis, distance: 6 days
]

descriptions = {
    1: "Starter Town: A quaint town nestled at the foot of the mountains, where every journey begins.",
    2: "Eldergrove: A mystical forest inhabited by ancient spirits, offering solace and wisdom to travelers.",
    3: "Crystal Peaks: Majestic mountains adorned with sparkling crystals, harboring secrets of the past.",
    4: "Dragon's Hollow: A desolate valley haunted by the remnants of mighty dragons, their presence felt in every shadow.",
    5: "Frostwind Citadel: A towering fortress carved from ice, home to fierce warriors and frost magic.",
    6: "Whispering Woods: Enchanted trees whisper secrets of forgotten lore, guiding wanderers with their eerie melodies.",
    7: "Mystic Falls: Cascading waterfalls imbued with arcane energy, said to grant visions to those who dare to gaze into their depths.",
    8: "Sunset Harbor: A bustling port city where traders from distant lands converge, bringing tales of adventure and riches.",
    9: "Ancient Ruins of Zephyr: Crumbling ruins of a once-great civilization, now shrouded in mystery and danger.",
    10: "Shadowvale Village: A secluded village hidden in the shadows, its inhabitants wary of outsiders and their own dark secrets.",
    11: "Grimreach Caverns: Dark caverns teeming with creatures of the abyss, where only the bravest dare to tread.",
    12: "Celestial City: A city floating among the clouds, its spires reaching towards the heavens, home to scholars and seekers of celestial knowledge.",
    13: "Thundering Steppes: Rolling plains where storms rage endlessly, a testament to the raw power of nature.",
    14: "Sands of Time Desert: Endless dunes whispering tales of forgotten empires buried beneath the sands.",
    15: "Serpent's Spine: A treacherous mountain range inhabited by colossal serpents, guarding ancient treasures hidden within their coils.",
    16: "Abyssal Depths: Unfathomable depths where darkness reigns supreme, home to creatures of nightmares.",
    17: "Stormwatch Keep: A fortress perched on the edge of a stormy sea, its towers standing vigilant against the forces of chaos.",
    18: "Emberwood Grove: A forest ablaze with the colors of autumn, where fire magic dances among the leaves.",
    19: "Shrouded Peaks: Mist-shrouded peaks where echoes of the past linger, beckoning travelers to uncover their secrets.",
    20: "Lost City of Atlantis: A legendary city submerged beneath the waves, said to hold untold riches and ancient artifacts of great power."
}

race_descriptions = {
    "human": ["Versatile and adaptable, humans are found in every corner of Arvantis, thriving in diverse environments and cultures.",
              [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]],
    
    "elf": ["Graceful and attuned to nature, elves make their homes in ancient forests, secluded groves, and mystical glades where the magic of the land flows freely.",
            [2, 6, 3]],
    
    "dwarf": ["Resilient and industrious, dwarves are known for their craftsmanship and love of the mountains. They carve out vast underground cities beneath the earth, mining precious metals and gems.",
              [3, 4, 18]],
    
    "orc": ["Fierce and tribal, orcs favor harsh environments such as rugged mountains, barren deserts, and untamed wilderness. They build formidable fortresses and conquer lands through brute strength.",
            [4, 14, 11]],
    
    "gnome": ["Inventive and curious, gnomes are drawn to places where knowledge and innovation flourish. They establish vibrant communities in bustling cities and hidden enclaves, delving into arcane mysteries and technological marvels.",
              [12, 1, 7]],
    
    "halfling": ["Friendly and carefree, halflings prefer the comforts of home and the pleasures of good company. They dwell in quaint villages nestled amidst fertile farmlands and rolling hills, living off the land and sharing tales of adventure.",
                 [1, 8, 10]],
    
    "dragonborn": ["Noble and proud, dragonborn are born warriors with a connection to ancient dragon heritage. They establish strongholds in rugged landscapes and seek to honor their draconic ancestors through deeds of valor.",
                   [4, 3, 17]],
    
    "tiefling": ["Mysterious and enigmatic, tieflings are often misunderstood due to their infernal ancestry. They find solace in hidden corners of the world, where they can pursue their own agendas away from prying eyes.",
                 [19, 16, 11]],
    
    "half-elf": ["Born of two worlds, half-elves navigate between human society and elven kinship, seeking belonging and acceptance wherever they roam. They often dwell in cosmopolitan cities and remote wilderness alike, embracing their dual heritage.",
                 [1, 2, 15]],
    
    "half-orc": ["Torn between two cultures, half-orcs forge their own path through strength and determination. They often find kinship among other outcasts, forming tight-knit communities on the fringes of society.",
                 [4, 10, 5]],
    
    "undead": ["Cursed and restless, the undead are beings trapped between life and death, their existence fueled by dark magic or vengeful spirits. They haunt desolate places and ancient crypts, seeking to fulfill their unending desires.",
               [11, 9, 16]],
    
    "fairy": ["Playful and mischievous, fairies flit through enchanted forests and hidden meadows, reveling in the beauty of the natural world. They make their homes in hidden glens and secret clearings, far from the prying eyes of mortals.",
              [6, 2, 15]],
    
    "centaur": ["Proud and noble, centaurs roam the open plains and lush meadows, their hooves pounding against the earth as they race beneath the open sky. They establish nomadic tribes and sacred hunting grounds, honoring the spirits of the land.",
                [13, 15, 6]],
    
    "celestial": ["Radiant and divine, celestials embody the virtues of justice and righteousness, serving as beacons of hope in dark times. They dwell in celestial realms beyond mortal ken, intervening in the affairs of mortals when the balance of the world is at stake.",
                  [12, 3, 20]],
    
    "demon": ["Twisted and malevolent, demons revel in chaos and destruction, their very presence warping the fabric of reality. They carve out domains in realms tainted by darkness, ruling over legions of fiendish minions with iron claws and fiery wrath.",
              [16, 10, 11]],

    "pixie": ["Whimsical and ethereal, pixies dance on the edges of dreams and reality, their laughter echoing through sun-dappled glades and moonlit clearings. They make their homes in hidden realms, where time flows differently and magic weaves its gentle embrace.",
              [6, 2, 15]],
              
    "angel": ["Pure and luminous, angels are beings of divine grace and virtue, their presence bringing comfort and solace to those in need. They reside in celestial realms, watching over mortals with benevolent eyes and guiding them towards the path of righteousness.",
              [12, 3, 20]],
    
    "dryad": ["Mysterious and elusive, dryads are spirits of the forest, bound to the ancient trees that shelter their sacred groves. They weave magic through the leaves and branches, protecting the natural world from harm and nurturing life with their gentle touch.",
              [6, 2, 18]]
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
    app.run(debug=True, host='0.0.0.0', port=5000)
