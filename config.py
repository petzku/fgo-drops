""" Contains config stuff for the scripts. Edit this to your heart's content. """

from typing import List

# if you want to store the json files in a subdirectory or something
PATH_PREFIX = ""

# you can add items to ignore here if you want
BLACKLIST: List[str] = []

# or here to ignore everything except these
# this one is for simplicity: stuff works if second line is commented
WHITELIST: List[str] = []
# WHITELIST = ["Eternal Ice", "Void's Dust", "Giant's Ring", "Aurora Steel"]

# show these items as output in terminal
OUTPUT: List[str] = ["Eternal Ice", "Void's Dust", "Giant's Ring", "Aurora Steel"]

# lower this if you want to show bad nodes (so you can tell your friends not to run them or whatever)
EFFICIENCY_THRESHOLD = 1

# === You can ignore stuff after this part ===

BASE_URL = "https://gamepress.gg/grandorder"
DROPS_FILE = PATH_PREFIX + "drops.json"

# we don't want to consider these because of the high APD bias
CLASSES = ("Saber", "Caster", "Lancer", "Archer", "Assassin", "Rider", "Berserker")
PREFIX_DROPS = ("Blaze of Wisdom - Gold", "Gem of", "Magic Gem of", "Secret Gem of")
POSTFIX_DROPS = ("Piece", "Monument")
BLACKLIST += [t + " " + c for t in PREFIX_DROPS for c in CLASSES]
BLACKLIST += [c + " " + t for t in POSTFIX_DROPS for c in CLASSES]
