from flask import *
import random
from map import generate_html_tree

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# scaling constants
current_location = 1
level_scaling_rate = 2
level = 100
endurance_scaling_rate = 5
strength_factor = 8
base_xp = 100
scaling_factor = 7

in_combat = False
is_resting = False
player_combat_count = 0

### USER INTERACTIONS ###


def moveCost(d):
    """Calculates the cost to move to a place"""
    global player_stats
    e = player.stats["endurance"]
    a = player.stats["agility"]

    return 100 * (d / (a + e))


def find_distance(a, b):
    """Finds the distance between two places"""
    for i in nodes:
        if i[0] == a or i[1] == a:
            if i[0] == b or i[1] == b:
                return i[2]
    return -1


locations = {
    # city name, visited status, and color
    1: ["Starter Town", "U", "#B28719"],
    2: ["Eldergrove", "U", "#3CB371"],
    3: ["Crystal Peaks", "U", "#ADD8E6"],
    4: ["Dragons Hollow", "U", "#8B0000"],
    5: ["Frostwind Citadel", "U", "#FFFFFF"],
    6: ["Whispering Woods", "U", "#228B22"],
    7: ["Mystic Falls", "U", "#4169E1"],
    8: ["Sunset Harbor", "U", "#FF4500"],
    9: ["Ancient Ruins of Zephyr", "U", "#DAA520"],
    10: ["Shadowvale Village", "U", "#4B0082"],
    11: ["Grimreach Caverns", "U", "#A0522D"],
    12: ["Celestial City", "U", "#FFFF00"],
    13: ["Thundering Steppes", "U", "#708090"],
    14: ["Sands of Time Desert", "U", "#F5DEB3"],
    15: ["Serpents Spine", "U", "#8A2BE2"],
    16: ["Abyssal Depths", "U", "#000080"],
    17: ["Stormwatch Keep", "U", "#00CED1"],
    18: ["Emberwood Grove", "U", "#8B4513"],
    19: ["Shrouded Peaks", "U", "#778899"],
    20: ["Lost City of Atlantis", "U", "#00FFFF"],
}

nodes = [
    [1, 2, 5],  # Starter Town to Eldergrove, distance: 5 days
    [1, 3, 8],  # Starter Town to Crystal Peaks, distance: 8 days
    [1, 4, 10],  # Starter Town to Dragon's Hollow, distance: 10 days
    [2, 5, 4],  # Eldergrove to Frostwind Citadel, distance: 4 days
    [2, 6, 3],  # Eldergrove to Whispering Woods, distance: 3 days
    [3, 7, 6],  # Crystal Peaks to Mystic Falls, distance: 6 days
    [3, 8, 7],  # Crystal Peaks to Sunset Harbor, distance: 7 days
    [4, 9, 12],  # Dragon's Hollow to Ancient Ruins of Zephyr, distance: 12 days
    [5, 10, 9],  # Frostwind Citadel to Shadowvale Village, distance: 9 days
    [5, 11, 5],  # Frostwind Citadel to Grimreach Caverns, distance: 5 days
    [6, 12, 8],  # Whispering Woods to Celestial City, distance: 8 days
    [6, 13, 6],  # Whispering Woods to Thundering Steppes, distance: 6 days
    [7, 14, 10],  # Mystic Falls to Sands of Time Desert, distance: 10 days
    [7, 15, 7],  # Mystic Falls to Serpent's Spine, distance: 7 days
    [8, 16, 12],  # Sunset Harbor to Abyssal Depths, distance: 12 days
    [8, 17, 9],  # Sunset Harbor to Stormwatch Keep, distance: 9 days
    [9, 18, 5],  # Ancient Ruins of Zephyr to Emberwood Grove, distance: 5 days
    [9, 19, 8],  # Ancient Ruins of Zephyr to Shrouded Peaks, distance: 8 days
    [10, 20, 15],  # Shadowvale Village to Lost City of Atlantis, distance: 15 days
    [11, 20, 13],  # Grimreach Caverns to Lost City of Atlantis, distance: 13 days
    [12, 20, 11],  # Celestial City to Lost City of Atlantis, distance: 11 days
    [13, 20, 12],  # Thundering Steppes to Lost City of Atlantis, distance: 12 days
    [14, 20, 14],  # Sands of Time Desert to Lost City of Atlantis, distance: 14 days
]
resting_areas = [1, 2, 7, 8, 12]

descriptions = {
    1: "A quaint town nestled at the foot of the mountains, where every journey begins.<br><span class='g'>Resting Area</span>",
    2: "A mystical forest inhabited by ancient spirits, offering solace and wisdom to travelers.<br><span class='g'>Resting Area</span>",
    3: "Majestic mountains adorned with sparkling crystals, harboring secrets of the past.",
    4: "A desolate valley haunted by the remnants of mighty dragons, their presence felt in every shadow.",
    5: "A towering fortress carved from ice, home to fierce warriors and frost magic.",
    6: "Enchanted trees whisper secrets of forgotten lore, guiding wanderers with their eerie melodies.",
    7: "Cascading waterfalls imbued with arcane energy, said to grant visions to those who dare to gaze into their depths.<br><span class='g'>Resting Area</span>",
    8: "A bustling port city where traders from distant lands converge, bringing tales of adventure and riches.<br><span class='g'>Resting Area</span>",
    9: "Crumbling ruins of a once-great civilization, now shrouded in mystery and danger.",
    10: "A secluded village hidden in the shadows, its inhabitants wary of outsiders and their own dark secrets.",
    11: "Dark caverns teeming with creatures of the abyss, where only the bravest dare to tread.",
    12: "A city floating among the clouds, its spires reaching towards the heavens, home to scholars and seekers of celestial knowledge.<br><span class='g'>Resting Area</span>",
    13: "Rolling plains where storms rage endlessly, a testament to the raw power of nature.",
    14: "Endless dunes whispering tales of forgotten empires buried beneath the sands.",
    15: "A treacherous mountain range inhabited by colossal serpents, guarding ancient treasures hidden within their coils.",
    16: "Unfathomable depths where darkness reigns supreme, home to creatures of nightmares.",
    17: "A fortress perched on the edge of a stormy sea, its towers standing vigilant against the forces of chaos.",
    18: "A forest ablaze with the colors of autumn, where fire magic dances among the leaves.",
    19: "Mist-shrouded peaks where echoes of the past linger, beckoning travelers to uncover their secrets.",
    20: "A legendary city submerged beneath the waves, said to hold untold riches and ancient artifacts of great power.",
}

race_descriptions = {
    "human": [
        "Versatile and adaptable, humans are found in every corner of Arvantis, thriving in diverse environments and cultures.",
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
    ],
    "elf": [
        "Graceful and attuned to nature, elves make their homes in ancient forests, secluded groves, and mystical glades where the magic of the land flows freely.",
        [2, 6, 3],
    ],
    "dwarf": [
        "Resilient and industrious, dwarves are known for their craftsmanship and love of the mountains. They carve out vast underground cities beneath the earth, mining precious metals and gems.",
        [3, 4, 18],
    ],
    "orc": [
        "Fierce and tribal, orcs favor harsh environments such as rugged mountains, barren deserts, and untamed wilderness. They build formidable fortresses and conquer lands through brute strength.",
        [4, 14, 11],
    ],
    "gnome": [
        "Inventive and curious, gnomes are drawn to places where knowledge and innovation flourish. They establish vibrant communities in bustling cities and hidden enclaves, delving into arcane mysteries and technological marvels.",
        [12, 1, 7],
    ],
    "halfling": [
        "Friendly and carefree, halflings prefer the comforts of home and the pleasures of good company. They dwell in quaint villages nestled amidst fertile farmlands and rolling hills, living off the land and sharing tales of adventure.",
        [1, 8, 10],
    ],
    "chinese dragonborn": [
        "Noble and proud, chinese dragonborn are born warriors with a connection to ancient dragon heritage. They establish strongholds in rugged landscapes and seek to honor their draconic ancestors through deeds of valor.",
        [4, 3, 17],
    ],
    "tiefling": [
        "Mysterious and enigmatic, tieflings are often misunderstood due to their infernal ancestry. They find solace in hidden corners of the world, where they can pursue their own agendas away from prying eyes.",
        [19, 16, 11],
    ],
    "half-elf": [
        "Born of two worlds, half-elves navigate between human society and elven kinship, seeking belonging and acceptance wherever they roam. They often dwell in cosmopolitan cities and remote wilderness alike, embracing their dual heritage.",
        [1, 2, 15],
    ],
    "half-orc": [
        "Torn between two cultures, half-orcs forge their own path through strength and determination. They often find kinship among other outcasts, forming tight-knit communities on the fringes of society.",
        [4, 10, 5],
    ],
    "undead": [
        "Cursed and restless, the undead are beings trapped between life and death, their existence fueled by dark magic or vengeful spirits. They haunt desolate places and ancient crypts, seeking to fulfill their unending desires.",
        [11, 9, 16],
    ],
    "fairy": [
        "Playful and mischievous, fairies flit through enchanted forests and hidden meadows, reveling in the beauty of the natural world. They make their homes in hidden glens and secret clearings, far from the prying eyes of mortals.",
        [6, 2, 15],
    ],
    "centaur": [
        "Proud and noble, centaurs roam the open plains and lush meadows, their hooves pounding against the earth as they race beneath the open sky. They establish nomadic tribes and sacred hunting grounds, honoring the spirits of the land.",
        [13, 15, 6],
    ],
    "celestial": [
        "Radiant and divine, celestials embody the virtues of justice and righteousness, serving as beacons of hope in dark times. They dwell in celestial realms beyond mortal ken, intervening in the affairs of mortals when the balance of the world is at stake.",
        [12, 3, 20],
    ],
    "demon": [
        "Twisted and malevolent, demons revel in chaos and destruction, their very presence warping the fabric of reality. They carve out domains in realms tainted by darkness, ruling over legions of fiendish minions with iron claws and fiery wrath.",
        [16, 10, 11],
    ],
    "pixie": [
        "Whimsical and ethereal, pixies dance on the edges of dreams and reality, their laughter echoing through sun-dappled glades and moonlit clearings. They make their homes in hidden realms, where time flows differently and magic weaves its gentle embrace.",
        [6, 2, 15],
    ],
    "angel": [
        "Pure and luminous, angels are beings of divine grace and virtue, their presence bringing comfort and solace to those in need. They reside in celestial realms, watching over mortals with benevolent eyes and guiding them towards the path of righteousness.",
        [12, 3, 20],
    ],
    "dryad": [
        "Mysterious and elusive, dryads are spirits of the forest, bound to the ancient trees that shelter their sacred groves. They weave magic through the leaves and branches, protecting the natural world from harm and nurturing life with their gentle touch.",
        [6, 2, 18],
    ],
}

race_stats = {
    "human": {
        "description": "Versatile and adaptable, humans are found in every corner of Arvantis, thriving in diverse environments and cultures.",
        "traits": [],
        "strength": (10 + 0) + level * (10 + 0),
        "endurance": (10 + 0) + level * (10 + 0),
        "mana": (10 + 0) + level * (10 + 0),
        "agility": (10 + 0) + level * (10 + 0),
    },
    "elf": {
        "description": "Graceful and attuned to nature, elves make their homes in ancient forests, secluded groves, and mystical glades where the magic of the land flows freely.",
        "traits": [
            ["Graceful", [["agility", 2], ["strength", -2], ["endurance", -2]]],
            ["Attuned to Nature", [["mana", 2]]],
        ],
        "strength": (10 - 5) + level * (10 - 5),
        "endurance": (10 - 5) + level * (10 - 5),
        "mana": (10 + 5) + level * (10 + 5),
        "agility": (10 + 5) + level * (10 + 5),
    },
    "dwarf": {
        "description": "Resilient and industrious, dwarves are known for their craftsmanship and love of the mountains. They carve out vast underground cities beneath the earth, mining precious metals and gems.",
        "traits": [["Resilient", [["strength", 2], ["endurance", 2], ["agility", -2]]]],
        "strength": (10 + 5) + level * (10 + 5),
        "endurance": (10 + 5) + level * (10 + 5),
        "mana": (10 + 0) + level * (10 + 0),
        "agility": (10 - 5) + level * (10 - 5),
    },
    "orc": {
        "description": "Fierce and tribal, orcs favor harsh environments such as rugged mountains, barren deserts, and untamed wilderness. They build formidable fortresses and conquer lands through brute strength.",
        "traits": [
            ["Fierce", [["strength", 4], ["endurance", 2], ["mana", -4]]],
            ["Tribal", [["agility", 2]]],
        ],
        "strength": (10 + 8) + level * (10 + 8),
        "endurance": (10 + 5) + level * (10 + 5),
        "mana": (10 - 8) + level * (10 - 8),
        "agility": (10 + 5) + level * (10 + 5),
    },
    "gnome": {
        "description": "Inventive and curious, gnomes are drawn to places where knowledge and innovation flourish. They establish vibrant communities in bustling cities and hidden enclaves, delving into arcane mysteries and technological marvels.",
        "traits": [
            ["Inventive", [["mana", 4], ["agility", 2], ["strength", -4]]],
            ["Curious", [["endurance", 2]]],
        ],
        "strength": (10 - 8) + level * (10 - 8),
        "endurance": (10 + 5) + level * (10 + 5),
        "mana": (10 + 8) + level * (10 + 8),
        "agility": (10 + 5) + level * (10 + 5),
    },
    "halfling": {
        "description": "Friendly and carefree, halflings prefer the comforts of home and the pleasures of good company. They dwell in quaint villages nestled amidst fertile farmlands and rolling hills, living off the land and sharing tales of adventure.",
        "traits": [
            ["Friendly", [["endurance", 2], ["mana", -2]]],
            ["Carefree", [["agility", 4], ["strength", -2]]],
        ],
        "strength": (10 - 5) + level * (10 - 5),
        "endurance": (10 + 5) + level * (10 + 5),
        "mana": (10 - 5) + level * (10 - 5),
        "agility": (10 + 8) + level * (10 + 8),
    },
    "chinese dragonborn": {
        "description": "Noble and proud, chinese dragonborn are born warriors with a connection to ancient dragon heritage. They establish strongholds in rugged landscapes and seek to honor their draconic ancestors through deeds of valor.",
        "traits": [
            ["Noble", [["strength", 4], ["endurance", 4], ["mana", 4]]],
            ["Proud", [["agility", 4]]],
        ],
        "strength": (10 + 8) + level * (10 + 8),
        "endurance": (10 + 8) + level * (10 + 8),
        "mana": (10 + 8) + level * (10 + 8),
        "agility": (10 + 8) + level * (10 + 8),
    },
    "tiefling": {
        "description": "Mysterious and enigmatic, tieflings are often misunderstood due to their infernal ancestry. They find solace in hidden corners of the world, where they can pursue their own agendas away from prying eyes.",
        "traits": [
            ["Mysterious", [["mana", 4], ["agility", 2], ["strength", -2]]],
            ["Enigmatic", [["endurance", 2]]],
        ],
        "strength": (10 - 5) + level * (10 - 5),
        "endurance": (10 + 5) + level * (10 + 5),
        "mana": (10 + 8) + level * (10 + 8),
        "agility": (10 + 5) + level * (10 + 5),
    },
    "half-elf": {
        "description": "Born of two worlds, half-elves navigate between human society and elven kinship, seeking belonging and acceptance wherever they roam. They often dwell in cosmopolitan cities and remote wilderness alike, embracing their dual heritage.",
        "traits": [
            ["Dual Heritage", [["mana", 2]]],
            ["Adaptable", [["strength", -2], ["endurance", -2]]],
        ],
        "strength": (10 - 5) + level * (10 - 5),
        "endurance": (10 - 5) + level * (10 - 5),
        "mana": (10 + 5) + level * (10 + 5),
        "agility": (10 + 0) + level * (10 + 0),
    },
    "half-orc": {
        "description": "Born of orc and human ancestry, half-orcs often face prejudice from both societies. They are renowned for their strength and resilience, often finding their place as warriors, laborers, or mercenaries.",
        "traits": [
            ["Orcish Strength", [["strength", 4], ["endurance", 2], ["mana", -2]]],
            ["Human Adaptability", [["agility", 2]]],
        ],
        "strength": (10 + 8) + level * (10 + 8),
        "endurance": (10 + 5) + level * (10 + 5),
        "mana": (10 - 5) + level * (10 - 5),
        "agility": (10 + 5) + level * (10 + 5),
    },
    "undead": {
        "description": "Cursed and forsaken, the undead walk the realm as echoes of their former selves. Bound by dark magic or unresolved grievances, they often haunt desolate places or serve dark masters.",
        "traits": [
            ["Cursed Existence", [["endurance", 4], ["mana", 2], ["agility", -2]]],
            ["Undead Resilience", [["strength", 2]]],
        ],
        "strength": (10 + 5) + level * (10 + 5),
        "endurance": (10 + 8) + level * (10 + 8),
        "mana": (10 + 5) + level * (10 + 5),
        "agility": (10 - 5) + level * (10 - 5),
    },
    "fairy": {
        "description": "Enigmatic and ethereal, fairies flit through the air on delicate wings, unseen by most mortals. They dwell in hidden realms of nature, where magic and whimsy hold sway.",
        "traits": [
            ["Ethereal Form", [["agility", 4], ["mana", 2], ["strength", -2]]],
            ["Fleeting Presence", [["endurance", -2]]],
        ],
        "strength": (10 - 5) + level * (10 - 5),
        "endurance": (10 - 5) + level * (10 - 5),
        "mana": (10 + 5) + level * (10 + 5),
        "agility": (10 + 8) + level * (10 + 8),
    },
    "centaur": {
        "description": "Proud and majestic, centaurs are half-human, half-horse beings who roam vast plains and wooded glens. They embody the spirit of freedom and are renowned for their speed and strength.",
        "traits": [
            ["Equine Grace", [["agility", 4], ["endurance", 2], ["mana", -2]]],
            ["Fleet-footed", [["strength", 2]]],
        ],
        "strength": (10 + 5) + level * (10 + 5),
        "endurance": (10 + 5) + level * (10 + 5),
        "mana": (10 - 5) + level * (10 - 5),
        "agility": (10 + 8) + level * (10 + 8),
    },
    "celestial": {
        "description": "Radiant and divine, celestials are beings of light and purity, serving as guardians of the heavens and protectors of mortal realms. They are imbued with celestial power and often intervene in the affairs of mortals to combat darkness and evil.",
        "traits": [
            ["Radiant Aura", [["mana", 4], ["endurance", 2], ["strength", -2]]],
            ["Divine Blessing", [["agility", 2]]],
        ],
        "strength": (10 - 5) + level * (10 - 5),
        "endurance": (10 + 5) + level * (10 + 5),
        "mana": (10 + 8) + level * (10 + 8),
        "agility": (10 + 5) + level * (10 + 5),
    },
    "demon": {
        "description": "Infernal and malevolent, demons hail from the depths of the Abyss, where chaos reigns and suffering knows no end. They delight in corruption and destruction, seeking to spread chaos and consume souls.",
        "traits": [
            ["Infernal Power", [["strength", 4], ["mana", 2], ["endurance", -2]]],
            ["Demonic Resilience", [["agility", 2]]],
        ],
        "strength": (10 + 8) + level * (10 + 8),
        "endurance": (10 - 5) + level * (10 - 5),
        "mana": (10 + 5) + level * (10 + 5),
        "agility": (10 + 5) + level * (10 + 5),
    },
    "pixie": {
        "description": "Playful and mischievous, pixies are tiny fey creatures with delicate wings and boundless energy. They inhabit enchanted forests and shimmering meadows, where they frolic among flowers and trick unsuspecting travelers.",
        "traits": [
            ["Fey Magic", [["mana", 4], ["agility", 2], ["strength", -2]]],
            ["Flighty Nature", [["endurance", -2]]],
        ],
        "strength": (10 - 5) + level * (10 - 5),
        "endurance": (10 - 5) + level * (10 - 5),
        "mana": (10 + 8) + level * (10 + 8),
        "agility": (10 + 5) + level * (10 + 5),
    },
    "angel": {
        "description": "Noble and celestial, angels are beings of pure light and virtue, serving as messengers of the divine and defenders of righteousness. They soar through the heavens on radiant wings, bringing hope and salvation to those in need.",
        "traits": [
            ["Divine Grace", [["mana", 4], ["endurance", 2], ["strength", -2]]],
            ["Radiant Wings", [["agility", 2]]],
        ],
        "strength": (10 - 5) + level * (10 - 5),
        "endurance": (10 + 5) + level * (10 + 5),
        "mana": (10 + 8) + level * (10 + 8),
        "agility": (10 + 5) + level * (10 + 5),
    },
    "dryad": {
        "description": "Enigmatic and elusive, dryads are forest spirits bound to the trees they inhabit. They are guardians of nature, nurturing the woodlands and protecting them from harm. They rarely interact with mortals, preferring the company of the ancient trees.",
        "traits": [
            ["Forest Bound", [["mana", 4], ["agility", 2], ["strength", -2]]],
            ["Nature's Blessing", [["endurance", 2]]],
        ],
        "strength": (10 - 5) + level * (10 - 5),
        "endurance": (10 + 5) + level * (10 + 5),
        "mana": (10 + 8) + level * (10 + 8),
        "agility": (10 + 5) + level * (10 + 5),
    },
}


@app.route("/racestats", methods=["POST"])
def racestats():
    r = request.args.get("race")
    return [
        race_stats[r]["strength"],
        race_stats[r]["endurance"],
        race_stats[r]["mana"],
        race_stats[r]["agility"],
        race_stats[r]["traits"],
    ]


class Player:
    """A player."""

    def __init__(self, name, race, mana, stamina, hp, level):
        """Constructs a player"""
        self.name = name
        self.race = race
        self.level = level
        self.xp = 0
        self.xp_required = base_xp + (self.level**2 * scaling_factor)

        self.max_hp = hp
        self.hp = self.max_hp
        self.max_mana = mana
        self.mana = self.max_mana
        self.max_stamina = stamina
        self.stamina = self.max_stamina
        self.raceStats = {
            "human": {
                "description": "Versatile and adaptable, humans are found in every corner of Arvantis, thriving in diverse environments and cultures.",
                "traits": [],
                "strength": (10 + 0) + self.level * (10 + 0),
                "endurance": (10 + 0) + self.level * (10 + 0),
                "mana": (10 + 0) + self.level * (10 + 0),
                "agility": (10 + 0) + self.level * (10 + 0),
            },
            "elf": {
                "description": "Graceful and attuned to nature, elves make their homes in ancient forests, secluded groves, and mystical glades where the magic of the land flows freely.",
                "traits": [
                    ["Graceful", [["agility", 2], ["strength", -2], ["endurance", -2]]],
                    ["Attuned to Nature", [["mana", 2]]],
                ],
                "strength": (10 - 5) + self.level * (10 - 5),
                "endurance": (10 - 5) + self.level * (10 - 5),
                "mana": (10 + 5) + self.level * (10 + 5),
                "agility": (10 + 5) + self.level * (10 + 5),
            },
            "dwarf": {
                "description": "Resilient and industrious, dwarves are known for their craftsmanship and love of the mountains. They carve out vast underground cities beneath the earth, mining precious metals and gems.",
                "traits": [
                    ["Resilient", [["strength", 2], ["endurance", 2], ["agility", -2]]]
                ],
                "strength": (10 + 5) + self.level * (10 + 5),
                "endurance": (10 + 5) + self.level * (10 + 5),
                "mana": (10 + 0) + self.level * (10 + 0),
                "agility": (10 - 5) + self.level * (10 - 5),
            },
            "orc": {
                "description": "Fierce and tribal, orcs favor harsh environments such as rugged mountains, barren deserts, and untamed wilderness. They build formidable fortresses and conquer lands through brute strength.",
                "traits": [
                    ["Fierce", [["strength", 4], ["endurance", 2], ["mana", -4]]],
                    ["Tribal", [["agility", 2]]],
                ],
                "strength": (10 + 8) + self.level * (10 + 8),
                "endurance": (10 + 5) + self.level * (10 + 5),
                "mana": (10 - 8) + self.level * (10 - 8),
                "agility": (10 + 5) + self.level * (10 + 5),
            },
            "gnome": {
                "description": "Inventive and curious, gnomes are drawn to places where knowledge and innovation flourish. They establish vibrant communities in bustling cities and hidden enclaves, delving into arcane mysteries and technological marvels.",
                "traits": [
                    ["Inventive", [["mana", 4], ["agility", 2], ["strength", -4]]],
                    ["Curious", [["endurance", 2]]],
                ],
                "strength": (10 - 8) + self.level * (10 - 8),
                "endurance": (10 + 5) + self.level * (10 + 5),
                "mana": (10 + 8) + self.level * (10 + 8),
                "agility": (10 + 5) + self.level * (10 + 5),
            },
            "halfling": {
                "description": "Friendly and carefree, halflings prefer the comforts of home and the pleasures of good company. They dwell in quaint villages nestled amidst fertile farmlands and rolling hills, living off the land and sharing tales of adventure.",
                "traits": [
                    ["Friendly", [["endurance", 2], ["mana", -2]]],
                    ["Carefree", [["agility", 4], ["strength", -2]]],
                ],
                "strength": (10 - 5) + self.level * (10 - 5),
                "endurance": (10 + 5) + self.level * (10 + 5),
                "mana": (10 - 5) + self.level * (10 - 5),
                "agility": (10 + 8) + self.level * (10 + 8),
            },
            "chinese dragonborn": {
                "description": "Noble and proud, chinese dragonborn are born warriors with a connection to ancient dragon heritage. They establish strongholds in rugged landscapes and seek to honor their draconic ancestors through deeds of valor.",
                "traits": [
                    ["Noble", [["strength", 4], ["endurance", 4], ["mana", 4]]],
                    ["Proud", [["agility", 4]]],
                ],
                "strength": (10 + 8) + self.level * (10 + 8),
                "endurance": (10 + 8) + self.level * (10 + 8),
                "mana": (10 + 8) + self.level * (10 + 8),
                "agility": (10 + 8) + self.level * (10 + 8),
            },
            "tiefling": {
                "description": "Mysterious and enigmatic, tieflings are often misunderstood due to their infernal ancestry. They find solace in hidden corners of the world, where they can pursue their own agendas away from prying eyes.",
                "traits": [
                    ["Mysterious", [["mana", 4], ["agility", 2], ["strength", -2]]],
                    ["Enigmatic", [["endurance", 2]]],
                ],
                "strength": (10 - 5) + self.level * (10 - 5),
                "endurance": (10 + 5) + self.level * (10 + 5),
                "mana": (10 + 8) + self.level * (10 + 8),
                "agility": (10 + 5) + self.level * (10 + 5),
            },
            "half-elf": {
                "description": "Born of two worlds, half-elves navigate between human society and elven kinship, seeking belonging and acceptance wherever they roam. They often dwell in cosmopolitan cities and remote wilderness alike, embracing their dual heritage.",
                "traits": [
                    ["Dual Heritage", [["mana", 2]]],
                    ["Adaptable", [["strength", -2], ["endurance", -2]]],
                ],
                "strength": (10 - 5) + self.level * (10 - 5),
                "endurance": (10 - 5) + self.level * (10 - 5),
                "mana": (10 + 5) + self.level * (10 + 5),
                "agility": (10 + 0) + self.level * (10 + 0),
            },
            "half-orc": {
                "description": "Born of orc and human ancestry, half-orcs often face prejudice from both societies. They are renowned for their strength and resilience, often finding their place as warriors, laborers, or mercenaries.",
                "traits": [
                    [
                        "Orcish Strength",
                        [["strength", 4], ["endurance", 2], ["mana", -2]],
                    ],
                    ["Human Adaptability", [["agility", 2]]],
                ],
                "strength": (10 + 8) + self.level * (10 + 8),
                "endurance": (10 + 5) + self.level * (10 + 5),
                "mana": (10 - 5) + self.level * (10 - 5),
                "agility": (10 + 5) + self.level * (10 + 5),
            },
            "undead": {
                "description": "Cursed and forsaken, the undead walk the realm as echoes of their former selves. Bound by dark magic or unresolved grievances, they often haunt desolate places or serve dark masters.",
                "traits": [
                    [
                        "Cursed Existence",
                        [["endurance", 4], ["mana", 2], ["agility", -2]],
                    ],
                    ["Undead Resilience", [["strength", 2]]],
                ],
                "strength": (10 + 5) + self.level * (10 + 5),
                "endurance": (10 + 8) + self.level * (10 + 8),
                "mana": (10 + 5) + self.level * (10 + 5),
                "agility": (10 - 5) + self.level * (10 - 5),
            },
            "fairy": {
                "description": "Enigmatic and ethereal, fairies flit through the air on delicate wings, unseen by most mortals. They dwell in hidden realms of nature, where magic and whimsy hold sway.",
                "traits": [
                    ["Ethereal Form", [["agility", 4], ["mana", 2], ["strength", -2]]],
                    ["Fleeting Presence", [["endurance", -2]]],
                ],
                "strength": (10 - 5) + self.level * (10 - 5),
                "endurance": (10 - 5) + self.level * (10 - 5),
                "mana": (10 + 5) + self.level * (10 + 5),
                "agility": (10 + 8) + self.level * (10 + 8),
            },
            "centaur": {
                "description": "Proud and majestic, centaurs are half-human, half-horse beings who roam vast plains and wooded glens. They embody the spirit of freedom and are renowned for their speed and strength.",
                "traits": [
                    ["Equine Grace", [["agility", 4], ["endurance", 2], ["mana", -2]]],
                    ["Fleet-footed", [["strength", 2]]],
                ],
                "strength": (10 + 5) + self.level * (10 + 5),
                "endurance": (10 + 5) + self.level * (10 + 5),
                "mana": (10 - 5) + self.level * (10 - 5),
                "agility": (10 + 8) + self.level * (10 + 8),
            },
            "celestial": {
                "description": "Radiant and divine, celestials are beings of light and purity, serving as guardians of the heavens and protectors of mortal realms. They are imbued with celestial power and often intervene in the affairs of mortals to combat darkness and evil.",
                "traits": [
                    ["Radiant Aura", [["mana", 4], ["endurance", 2], ["strength", -2]]],
                    ["Divine Blessing", [["agility", 2]]],
                ],
                "strength": (10 - 5) + self.level * (10 - 5),
                "endurance": (10 + 5) + self.level * (10 + 5),
                "mana": (10 + 8) + self.level * (10 + 8),
                "agility": (10 + 5) + self.level * (10 + 5),
            },
            "demon": {
                "description": "Infernal and malevolent, demons hail from the depths of the Abyss, where chaos reigns and suffering knows no end. They delight in corruption and destruction, seeking to spread chaos and consume souls.",
                "traits": [
                    [
                        "Infernal Power",
                        [["strength", 4], ["mana", 2], ["endurance", -2]],
                    ],
                    ["Demonic Resilience", [["agility", 2]]],
                ],
                "strength": (10 + 8) + self.level * (10 + 8),
                "endurance": (10 - 5) + self.level * (10 - 5),
                "mana": (10 + 5) + self.level * (10 + 5),
                "agility": (10 + 5) + self.level * (10 + 5),
            },
            "pixie": {
                "description": "Playful and mischievous, pixies are tiny fey creatures with delicate wings and boundless energy. They inhabit enchanted forests and shimmering meadows, where they frolic among flowers and trick unsuspecting travelers.",
                "traits": [
                    ["Fey Magic", [["mana", 4], ["agility", 2], ["strength", -2]]],
                    ["Flighty Nature", [["endurance", -2]]],
                ],
                "strength": (10 - 5) + self.level * (10 - 5),
                "endurance": (10 - 5) + self.level * (10 - 5),
                "mana": (10 + 8) + self.level * (10 + 8),
                "agility": (10 + 5) + self.level * (10 + 5),
            },
            "angel": {
                "description": "Noble and celestial, angels are beings of pure light and virtue, serving as messengers of the divine and defenders of righteousness. They soar through the heavens on radiant wings, bringing hope and salvation to those in need.",
                "traits": [
                    ["Divine Grace", [["mana", 4], ["endurance", 2], ["strength", -2]]],
                    ["Radiant Wings", [["agility", 2]]],
                ],
                "strength": (10 - 5) + self.level * (10 - 5),
                "endurance": (10 + 5) + self.level * (10 + 5),
                "mana": (10 + 8) + self.level * (10 + 8),
                "agility": (10 + 5) + self.level * (10 + 5),
            },
            "dryad": {
                "description": "Enigmatic and elusive, dryads are forest spirits bound to the trees they inhabit. They are guardians of nature, nurturing the woodlands and protecting them from harm. They rarely interact with mortals, preferring the company of the ancient trees.",
                "traits": [
                    ["Forest Bound", [["mana", 4], ["agility", 2], ["strength", -2]]],
                    ["Nature's Blessing", [["endurance", 2]]],
                ],
                "strength": (10 - 5) + self.level * (10 - 5),
                "endurance": (10 + 5) + self.level * (10 + 5),
                "mana": (10 + 8) + self.level * (10 + 8),
                "agility": (10 + 5) + self.level * (10 + 5),
            },
        }
        self.stats = self.raceStats[race]

    def level_up(self):
        """Levels up the player"""
        self.level += 1
        self.xp = 0
        # Adjust stats, HP, mana, etc. based on level increase
        self.stats_update()

    def stats_update(self):
        """Update the player stats"""
        self.raceStats = {
            "human": {
                "description": "Versatile and adaptable, humans are found in every corner of Arvantis, thriving in diverse environments and cultures.",
                "traits": [],
                "strength": (10 + 0) + self.level * (10 + 0),
                "endurance": (10 + 0) + self.level * (10 + 0),
                "mana": (10 + 0) + self.level * (10 + 0),
                "agility": (10 + 0) + self.level * (10 + 0),
            },
            "elf": {
                "description": "Graceful and attuned to nature, elves make their homes in ancient forests, secluded groves, and mystical glades where the magic of the land flows freely.",
                "traits": [
                    ["Graceful", [["agility", 2], ["strength", -2], ["endurance", -2]]],
                    ["Attuned to Nature", [["mana", 2]]],
                ],
                "strength": (10 - 5) + self.level * (10 - 5),
                "endurance": (10 - 5) + self.level * (10 - 5),
                "mana": (10 + 5) + self.level * (10 + 5),
                "agility": (10 + 5) + self.level * (10 + 5),
            },
            "dwarf": {
                "description": "Resilient and industrious, dwarves are known for their craftsmanship and love of the mountains. They carve out vast underground cities beneath the earth, mining precious metals and gems.",
                "traits": [
                    ["Resilient", [["strength", 2], ["endurance", 2], ["agility", -2]]]
                ],
                "strength": (10 + 5) + self.level * (10 + 5),
                "endurance": (10 + 5) + self.level * (10 + 5),
                "mana": (10 + 0) + self.level * (10 + 0),
                "agility": (10 - 5) + self.level * (10 - 5),
            },
            "orc": {
                "description": "Fierce and tribal, orcs favor harsh environments such as rugged mountains, barren deserts, and untamed wilderness. They build formidable fortresses and conquer lands through brute strength.",
                "traits": [
                    ["Fierce", [["strength", 4], ["endurance", 2], ["mana", -4]]],
                    ["Tribal", [["agility", 2]]],
                ],
                "strength": (10 + 8) + self.level * (10 + 8),
                "endurance": (10 + 5) + self.level * (10 + 5),
                "mana": (10 - 8) + self.level * (10 - 8),
                "agility": (10 + 5) + self.level * (10 + 5),
            },
            "gnome": {
                "description": "Inventive and curious, gnomes are drawn to places where knowledge and innovation flourish. They establish vibrant communities in bustling cities and hidden enclaves, delving into arcane mysteries and technological marvels.",
                "traits": [
                    ["Inventive", [["mana", 4], ["agility", 2], ["strength", -4]]],
                    ["Curious", [["endurance", 2]]],
                ],
                "strength": (10 - 8) + self.level * (10 - 8),
                "endurance": (10 + 5) + self.level * (10 + 5),
                "mana": (10 + 8) + self.level * (10 + 8),
                "agility": (10 + 5) + self.level * (10 + 5),
            },
            "halfling": {
                "description": "Friendly and carefree, halflings prefer the comforts of home and the pleasures of good company. They dwell in quaint villages nestled amidst fertile farmlands and rolling hills, living off the land and sharing tales of adventure.",
                "traits": [
                    ["Friendly", [["endurance", 2], ["mana", -2]]],
                    ["Carefree", [["agility", 4], ["strength", -2]]],
                ],
                "strength": (10 - 5) + self.level * (10 - 5),
                "endurance": (10 + 5) + self.level * (10 + 5),
                "mana": (10 - 5) + self.level * (10 - 5),
                "agility": (10 + 8) + self.level * (10 + 8),
            },
            "chinese dragonborn": {
                "description": "Noble and proud, chinese dragonborn are born warriors with a connection to ancient dragon heritage. They establish strongholds in rugged landscapes and seek to honor their draconic ancestors through deeds of valor.",
                "traits": [
                    ["Noble", [["strength", 4], ["endurance", 4], ["mana", 4]]],
                    ["Proud", [["agility", 4]]],
                ],
                "strength": (10 + 8) + self.level * (10 + 8),
                "endurance": (10 + 8) + self.level * (10 + 8),
                "mana": (10 + 8) + self.level * (10 + 8),
                "agility": (10 + 8) + self.level * (10 + 8),
            },
            "tiefling": {
                "description": "Mysterious and enigmatic, tieflings are often misunderstood due to their infernal ancestry. They find solace in hidden corners of the world, where they can pursue their own agendas away from prying eyes.",
                "traits": [
                    ["Mysterious", [["mana", 4], ["agility", 2], ["strength", -2]]],
                    ["Enigmatic", [["endurance", 2]]],
                ],
                "strength": (10 - 5) + self.level * (10 - 5),
                "endurance": (10 + 5) + self.level * (10 + 5),
                "mana": (10 + 8) + self.level * (10 + 8),
                "agility": (10 + 5) + self.level * (10 + 5),
            },
            "half-elf": {
                "description": "Born of two worlds, half-elves navigate between human society and elven kinship, seeking belonging and acceptance wherever they roam. They often dwell in cosmopolitan cities and remote wilderness alike, embracing their dual heritage.",
                "traits": [
                    ["Dual Heritage", [["mana", 2]]],
                    ["Adaptable", [["strength", -2], ["endurance", -2]]],
                ],
                "strength": (10 - 5) + self.level * (10 - 5),
                "endurance": (10 - 5) + self.level * (10 - 5),
                "mana": (10 + 5) + self.level * (10 + 5),
                "agility": (10 + 0) + self.level * (10 + 0),
            },
            "half-orc": {
                "description": "Born of orc and human ancestry, half-orcs often face prejudice from both societies. They are renowned for their strength and resilience, often finding their place as warriors, laborers, or mercenaries.",
                "traits": [
                    [
                        "Orcish Strength",
                        [["strength", 4], ["endurance", 2], ["mana", -2]],
                    ],
                    ["Human Adaptability", [["agility", 2]]],
                ],
                "strength": (10 + 8) + self.level * (10 + 8),
                "endurance": (10 + 5) + self.level * (10 + 5),
                "mana": (10 - 5) + self.level * (10 - 5),
                "agility": (10 + 5) + self.level * (10 + 5),
            },
            "undead": {
                "description": "Cursed and forsaken, the undead walk the realm as echoes of their former selves. Bound by dark magic or unresolved grievances, they often haunt desolate places or serve dark masters.",
                "traits": [
                    [
                        "Cursed Existence",
                        [["endurance", 4], ["mana", 2], ["agility", -2]],
                    ],
                    ["Undead Resilience", [["strength", 2]]],
                ],
                "strength": (10 + 5) + self.level * (10 + 5),
                "endurance": (10 + 8) + self.level * (10 + 8),
                "mana": (10 + 5) + self.level * (10 + 5),
                "agility": (10 - 5) + self.level * (10 - 5),
            },
            "fairy": {
                "description": "Enigmatic and ethereal, fairies flit through the air on delicate wings, unseen by most mortals. They dwell in hidden realms of nature, where magic and whimsy hold sway.",
                "traits": [
                    ["Ethereal Form", [["agility", 4], ["mana", 2], ["strength", -2]]],
                    ["Fleeting Presence", [["endurance", -2]]],
                ],
                "strength": (10 - 5) + self.level * (10 - 5),
                "endurance": (10 - 5) + self.level * (10 - 5),
                "mana": (10 + 5) + self.level * (10 + 5),
                "agility": (10 + 8) + self.level * (10 + 8),
            },
            "centaur": {
                "description": "Proud and majestic, centaurs are half-human, half-horse beings who roam vast plains and wooded glens. They embody the spirit of freedom and are renowned for their speed and strength.",
                "traits": [
                    ["Equine Grace", [["agility", 4], ["endurance", 2], ["mana", -2]]],
                    ["Fleet-footed", [["strength", 2]]],
                ],
                "strength": (10 + 5) + self.level * (10 + 5),
                "endurance": (10 + 5) + self.level * (10 + 5),
                "mana": (10 - 5) + self.level * (10 - 5),
                "agility": (10 + 8) + self.level * (10 + 8),
            },
            "celestial": {
                "description": "Radiant and divine, celestials are beings of light and purity, serving as guardians of the heavens and protectors of mortal realms. They are imbued with celestial power and often intervene in the affairs of mortals to combat darkness and evil.",
                "traits": [
                    ["Radiant Aura", [["mana", 4], ["endurance", 2], ["strength", -2]]],
                    ["Divine Blessing", [["agility", 2]]],
                ],
                "strength": (10 - 5) + self.level * (10 - 5),
                "endurance": (10 + 5) + self.level * (10 + 5),
                "mana": (10 + 8) + self.level * (10 + 8),
                "agility": (10 + 5) + self.level * (10 + 5),
            },
            "demon": {
                "description": "Infernal and malevolent, demons hail from the depths of the Abyss, where chaos reigns and suffering knows no end. They delight in corruption and destruction, seeking to spread chaos and consume souls.",
                "traits": [
                    [
                        "Infernal Power",
                        [["strength", 4], ["mana", 2], ["endurance", -2]],
                    ],
                    ["Demonic Resilience", [["agility", 2]]],
                ],
                "strength": (10 + 8) + self.level * (10 + 8),
                "endurance": (10 - 5) + self.level * (10 - 5),
                "mana": (10 + 5) + self.level * (10 + 5),
                "agility": (10 + 5) + self.level * (10 + 5),
            },
            "pixie": {
                "description": "Playful and mischievous, pixies are tiny fey creatures with delicate wings and boundless energy. They inhabit enchanted forests and shimmering meadows, where they frolic among flowers and trick unsuspecting travelers.",
                "traits": [
                    ["Fey Magic", [["mana", 4], ["agility", 2], ["strength", -2]]],
                    ["Flighty Nature", [["endurance", -2]]],
                ],
                "strength": (10 - 5) + self.level * (10 - 5),
                "endurance": (10 - 5) + self.level * (10 - 5),
                "mana": (10 + 8) + self.level * (10 + 8),
                "agility": (10 + 5) + self.level * (10 + 5),
            },
            "angel": {
                "description": "Noble and celestial, angels are beings of pure light and virtue, serving as messengers of the divine and defenders of righteousness. They soar through the heavens on radiant wings, bringing hope and salvation to those in need.",
                "traits": [
                    ["Divine Grace", [["mana", 4], ["endurance", 2], ["strength", -2]]],
                    ["Radiant Wings", [["agility", 2]]],
                ],
                "strength": (10 - 5) + self.level * (10 - 5),
                "endurance": (10 + 5) + self.level * (10 + 5),
                "mana": (10 + 8) + self.level * (10 + 8),
                "agility": (10 + 5) + self.level * (10 + 5),
            },
            "dryad": {
                "description": "Enigmatic and elusive, dryads are forest spirits bound to the trees they inhabit. They are guardians of nature, nurturing the woodlands and protecting them from harm. They rarely interact with mortals, preferring the company of the ancient trees.",
                "traits": [
                    ["Forest Bound", [["mana", 4], ["agility", 2], ["strength", -2]]],
                    ["Nature's Blessing", [["endurance", 2]]],
                ],
                "strength": (10 - 5) + self.level * (10 - 5),
                "endurance": (10 + 5) + self.level * (10 + 5),
                "mana": (10 + 8) + self.level * (10 + 8),
                "agility": (10 + 5) + self.level * (10 + 5),
            },
        }
        player_stats = self.raceStats[self.race]

        self.stats = player_stats

        mana = 100 + player_stats["mana"] * level_scaling_rate
        stamina = 200 + player_stats["endurance"] * endurance_scaling_rate
        xp_required = base_xp + (self.level**2 * scaling_factor)
        hp = (
            100
            + (player_stats["endurance"] * endurance_scaling_rate)
            + (level * level_scaling_rate)
            + (player_stats["strength"] * strength_factor)
        )

        self.xp = 0
        self.xp_required = xp_required
        self.max_hp = hp
        self.hp = self.max_hp
        self.max_mana = mana
        self.mana = self.max_mana
        self.max_stamina = stamina
        self.stamina = self.max_stamina

    def gain_xp(self, amount):
        """Gives the player experience points"""
        self.xp += amount
        if self.xp >= self.xp_required:
            self.level_up()

    def take_damage(self, damage):
        """Decreases the player's health"""
        self.hp -= damage


def reset_visited(l):
    """Resets a visited place"""
    for i in l:
        l[i][1] = "U"
    return l


def find_neighbors(x):  # takes in variable for reference
    """Finds the neighbours of a node"""
    neighbors = []
    for node in nodes:
        if node[0] == x or node[1] == x:
            neighbors.append(locations[[i for i in node if i != x][0]][0])
    return neighbors


def find_neighborsindex(x):  # takes in variable for reference
    """Finds the neighbours of a node, but returns the indices for those neighbours"""
    neighbors = []
    for node in nodes:
        if node[0] == x or node[1] == x:
            neighbors.append([i for i in node if i != x][0])
    return neighbors


player = 0


@app.route("/", methods=["GET", "POST"])
def index():
    global in_combat
    global player_combat_count
    in_combat = False
    player_combat_count = 0
    try:
        global current_location
        global locations
        global mana
        global stamina
        global maxmana
        global maxstamina
        global xp
        global xp_required
        global hp
        global hpmax
        global player
        if "name" in session and "race" in session:
            return render_template(
                "game.html",
                name=session["name"],
                race=session["race"],
                option_stats={
                    "mana": [player.mana, player.max_mana],
                    "stamina": [player.stamina, player.max_stamina],
                },
                level=player.level,
                xp=player.xp,
                xpmax=player.xp_required,
                hp=player.hp,
                hpmax=player.max_hp,
            )
        elif request.method == "POST":
            session["name"] = request.form["name"]
            session["race"] = request.form["race"]
            current_location = random.choice(race_descriptions[session["race"]][1])
            locations = reset_visited(locations)
            locations[current_location][1] = "V"
            mana = 100 + race_stats[session["race"]]["mana"] * level_scaling_rate
            stamina = (
                200 + race_stats[session["race"]]["endurance"] * endurance_scaling_rate
            )
            maxmana = 100 + race_stats[session["race"]]["mana"] * level_scaling_rate
            maxstamina = (
                200 + race_stats[session["race"]]["endurance"] * endurance_scaling_rate
            )
            xp = 0
            xp_required = base_xp + (level**2 * scaling_factor)
            hp = (
                100
                + (race_stats[session["race"]]["endurance"] * endurance_scaling_rate)
                + (level * level_scaling_rate)
                + (race_stats[session["race"]]["strength"] * strength_factor)
            )
            hpmax = (
                100
                + (race_stats[session["race"]]["endurance"] * endurance_scaling_rate)
                + (level * level_scaling_rate)
                + (race_stats[session["race"]]["strength"] * strength_factor)
            )
            player = Player(session["name"], session["race"], mana, stamina, hp, level)
            return redirect(url_for("game"))
        else:
            return render_template("signup.html")
    except Exception as e:
        print(e)
        session.clear()
        return redirect(url_for("index"))


@app.route("/endsession")
def endsession():
    session.clear()
    return redirect(url_for("index"))


@app.route("/level", methods=["POST"])
def levelss():
    if request.method == "GET":
        return redirect(url_for("index"))
    else:
        global player
        player.level_up()
        return str(player.level)


@app.route("/game")
def game():
    global in_combat
    global player_combat_count
    in_combat = False
    player_combat_count = 0
    try:
        # session.clear()
        if "name" in session and "race" in session:
            return render_template(
                "game.html",
                name=session["name"],
                race=session["race"],
                option_stats={
                    "mana": [player.mana, player.max_mana],
                    "stamina": [player.stamina, player.max_stamina],
                },
                level=player.level,
                xp=player.xp,
                xpmax=player.xp_required,
                hp=player.hp,
                hpmax=player.max_hp,
            )
        else:
            return redirect(url_for("index"))
    except Exception as e:
        print(e)
        session.clear()
        return redirect(url_for("index"))


@app.route("/find_neighbors", methods=["POST"])
def return_neighbors():
    neighbors = find_neighbors(current_location)
    neighborsindex = find_neighborsindex(current_location)
    form = ""
    for n, i in enumerate(neighbors):
        costToMove = moveCost(find_distance(current_location, neighborsindex[n]))
        if in_combat:
            disable = True
        else:
            if costToMove > player.stamina:
                disable = True
            else:
                disable = False
        if locations[neighborsindex[n]][1] == "U":
            cnew = " new!"
        else:
            cnew = ""
        form += f"""<button class="locbutton disable-{disable}" id="{i}" onclick='moveto("{i}")'>{neighborsindex[n]} - {i} <span id='r'>{cnew}</span></button>"""
    return form


@app.route("/location", methods=["POST"])
def return_location():
    return f"<span style='color: {locations[current_location][2]}'>{locations[current_location][0]}</span>"


@app.route("/getstats", methods=["POST"])
def getstats():
    return list(
        map(
            int,
            [
                player.hp,
                player.max_hp,
                player.mana,
                player.max_mana,
                player.stamina,
                player.max_stamina,
                player.xp,
                player.xp_required,
            ],
        )
    )


@app.route("/getmap", methods=["POST"])
def getmap():
    m = generate_html_tree(locations, nodes, current_location)
    return m


@app.route("/dsc", methods=["POST"])
def getdsc():
    n = request.args.get("n")
    return descriptions[int(n)]


@app.route("/fd", methods=["POST"])
def getl():
    if in_combat:
        return "no"

    else:
        s = request.args.get("s")
        t = request.args.get("t")
        if s == "CURRENT":
            s = current_location
        return f"{str(find_distance(int(s), int(t)))}KM"


@app.route("/getlvl", methods=["POST"])
def gggg():
    global player
    return str(player.level)


@app.route("/moveto", methods=["POST"])
def move_to():
    if in_combat:
        return "no bueno"
    global current_location
    newlocation = request.args.get("loc")
    for i in locations:
        if newlocation in locations[i]:
            for n in nodes:
                if n[0] == i or n[1] == i:
                    if n[0] == current_location or n[1] == current_location:
                        distance = n[2]
                        cost = moveCost(distance)
                        if player.stamina >= cost:
                            current_location = i
                            locations[i][1] = "V"
                            player.stamina -= cost
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

# player combat


attacks = {
    "Slash": {"damage": 20, "cost": 5},
    "Stab": {"damage": 40, "cost": 10},
    "Mana Blast": {"damage": 80, "cost": 20},
}

monsters = {
    "Goblin": {"health": 50, "damage": 10, "defense": 5, "boss": False},
    "Orc": {"health": 80, "damage": 15, "defense": 8, "boss": False},
    "Dragon": {"health": 200, "damage": 30, "defense": 20, "boss": True},
    "Skeleton": {"health": 40, "damage": 8, "defense": 3, "boss": False},
    "Zombie": {"health": 70, "damage": 12, "defense": 6, "boss": False},
    "Werewolf": {"health": 100, "damage": 18, "defense": 10, "boss": False},
    "Kraken": {"health": 250, "damage": 35, "defense": 25, "boss": True},
    "Giant Spider": {"health": 60, "damage": 12, "defense": 6, "boss": False},
    "Vampire": {"health": 120, "damage": 20, "defense": 15, "boss": False},
    "Wraith": {"health": 90, "damage": 16, "defense": 12, "boss": False},
    "Minotaur": {"health": 150, "damage": 25, "defense": 18, "boss": False},
    "Banshee": {"health": 80, "damage": 14, "defense": 8, "boss": False},
    "Hydra": {"health": 180, "damage": 28, "defense": 22, "boss": True},
    "Demon": {"health": 160, "damage": 22, "defense": 16, "boss": False},
    "Specter": {"health": 100, "damage": 18, "defense": 12, "boss": False},
    "Cyclops": {"health": 200, "damage": 30, "defense": 20, "boss": False},
    "Ghost": {"health": 70, "damage": 14, "defense": 8, "boss": False},
}

nonboss = ["Goblin", "Orc", "Skeleton", "Zombie", "Werewolf", "Giant Spider", "Vampire", "Wraith", "Minotaur", "Banshee", "Specter", "Cyclops", "Ghost"]
boss = ["Dragon", "Kraken", "Hydra", "Demon"]

current_combat = 0

# every 3 player combats, encounter a boss


class Combat:
    """The combat state"""

    def __init__(self, hp, m, mlevel, pas, cas) -> None:
        """Creates a combat state"""
        self.turn = 0  # player
        self.enemyhp = hp * (mlevel * 2 + 3) / 2
        self.monster = m
        self.level = mlevel
        self.pas = pas
        self.cas = cas


bossrn = False

@app.route("/resting", methods=["POST"])
def rest():
    if not in_combat and current_location in resting_areas:
        rm = player.max_mana * 0.02
        rs = player.max_stamina * 0.02
        rh = player.max_hp * 0.02
        if player.mana < player.max_mana:
            if player.mana + player.max_mana * 0.02 > player.max_mana:
                player.mana = player.max_mana
                rm = player.max_mana = player.mana
            else:
                player.mana += player.max_mana * 0.02
        if player.stamina < player.max_stamina:
            if player.stamina + player.max_stamina * 0.02 > player.max_stamina:
                player.stamina = player.max_stamina
                rs = player.max_stamina - stamina
            else:
                player.stamina += player.max_stamina * 0.02
        if player.hp < player.max_hp:
            if player.hp + player.max_hp * 0.02 > player.max_hp:
                player.hp = player.max_hp
                rh = player.max_hp - player.hp
            else:
                player.hp += player.max_hp * 0.02
        return "rest"
    elif in_combat:
        return "in combat"
    else:
        return "idle"
    


@app.route("/combat", methods=["POST"])
def combat():
    global current_combat
    global in_combat
    global player_combat_count
    global player
    global bossrn
    state = request.args.get("state")
    a = request.args.get("attack")
    data = []
    if state == "start" and in_combat == False:
        in_combat = True
        data.append("confirmed")
        if player_combat_count == 4:
            bossrn = True
            player_combat_count = 0
            monster = random.choice(boss)
            bosss = "boss monster "
            mlevel = player.level
        else:
            player_combat_count += 1
            monster = random.choice(nonboss)
            mlevel = random.randint(max(1, int(player.level/2)), player.level)
            bosss = ""
        pas = {}
        for a in attacks:
            pas[a] = (attacks[a]["damage"]+10) * ((player.level * 2 + 1) / 2)
        cas = {}
        for a in attacks:
            cas[a] = attacks[a]["cost"] * ((player.level) / 2)
        current_combat = Combat(monsters[monster]["health"], monster, mlevel, pas, cas)
        data.append(
            f"you have encountered a level {mlevel} {bosss}{monster}!<br><span class='g'>{current_combat.enemyhp}HP</span>"
        )
        l = ""
        for a in attacks:
            if a == "Mana Blast":
                if attacks[a]["cost"] > player.mana:
                    l += f"""<button class='disable-True' onclick='sendattack(this)' id='{a}'>{a} - {pas[a]} DMG ({cas[a]})</button>"""
                else:
                    l += f"""<button class='disable-False' onclick='sendattack(this)' id='{a}'>{a} - {pas[a]} DMG ({cas[a]})</button>"""

            else:
                if attacks[a]["cost"] > player.stamina:
                    l += f"""<button class='disable-True' onclick='sendattack(this)' id='{a}'>{a} - {pas[a]} DMG ({cas[a]})</button>"""
                else:
                    l += f"""<button class='disable-False' onclick='sendattack(this)' id='{a}'>{a} - {pas[a]} DMG ({cas[a]})</button>"""
        data.append(l)
        return data
    elif state == "start" and in_combat == True:
        return "occupied"
    elif a:
        pas = current_combat.pas
        cas = current_combat.cas

        data.append("confirmed")
        go = False
        if a == "Mana Blast":
            if player.mana >= cas[a]:
                go = True
                player.mana -= cas[a]
                current_combat.enemyhp -= pas[a]
        else:
            if player.stamina >= cas[a]:
                go = True
                player.stamina -= cas[a]
                current_combat.enemyhp -= pas[a]

    

        if current_combat.enemyhp <= 0:
            data.append("monster defeated!")
            data.append("Combat over!")
            in_combat = False
            player.xp += monsters[current_combat.monster]["health"] * ((current_combat.level)/2)
            if player.xp >= player.xp_required:
                req = player.xp_required
                curxp = player.xp
                newxp = req - curxp
                player.level_up()
                player.xp = abs(newxp)
            if (
                cas["Slash"] > player.stamina
                and cas["Stab"] > player.stamina
                and cas["Mana Blast"] > player.mana
            ):
                session.clear()
                return "game over"
            return data
        else:
            data.append(
                f"{current_combat.monster} Current health: <br><span class='g'>{current_combat.enemyhp}HP</span>"
            )
            l = ""

            if go:
                rng = random.random()
                if rng <= 1 and rng >= .8:
                    dmg = (
                        (
                            monsters[current_combat.monster]["damage"]
                            * 5
                        )
                        * (current_combat.level + 1)
                        / 2
                    )
                    player.hp -= dmg
                    l += (
                        f"""{current_combat.monster} hit the player with crit for {int(dmg)}HP!<br>"""
                    )
                elif rng == .5:
                    l += (
                        f"""ATtack missed!<br>"""
                    )
                else:
                    dmg = (
                        (
                            monsters[current_combat.monster]["damage"]
                            * 3
                        )
                        * (current_combat.level + 1)
                        / 2
                    )
                    player.hp -= dmg
                    l += (
                        f"""{current_combat.monster} hit the player for {int(dmg)}HP!<br>"""
                    )

            if (
                cas["Slash"] > player.stamina
                and cas["Stab"] > player.stamina
                and cas["Mana Blast"] > player.mana
            ):
                session.clear()
                return "game over"

            if player.hp <= 0:
                session.clear()
                return "game over"

            for a in attacks:
                if a == "Mana Blast":
                    if cas[a] > player.mana:
                        l += f"""<button class='disable-True' onclick='sendattack(this)' id='{a}'>{a} - {pas[a]} DMG ({cas[a]})</button>"""
                    else:
                        l += f"""<button class='disable-False' onclick='sendattack(this)' id='{a}'>{a} - {pas[a]} DMG ({cas[a]})</button>"""
                else:
                    if cas[a] > player.stamina:
                        l += f"""<button class='disable-True' onclick='sendattack(this)' id='{a}'>{a} - {pas[a]} DMG ({cas[a]})</button>"""
                    else:
                        l += f"""<button class='disable-False' onclick='sendattack(this)' id='{a}'>{a} - {pas[a]} DMG ({cas[a]})</button>"""
            data.append(l)
            return data


if __name__ == "__main__":
    app.jinja_env.cache = {}
    app.jinja_env.auto_reload = True
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.run(debug=True, host="0.0.0.0", port=5000)
