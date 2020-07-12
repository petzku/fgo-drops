#!/usr/bin/env python3

"""
Figure out most efficient places for farming materials in FGO.

Use drop data from Gamepress. Calculate APD values ourselves for higher
precision. Node efficiency takes into account all materials, but not EXP,
pieces/monuments, QP or gems.
NOTE: gem consideration may change.

Best node for material X is determined to be not its best single APD node,
but the highest total AP efficient node that drops that material.
"""

import json
from typing import Dict, Tuple, List, Any
from config import PATH_PREFIX, DROPS_FILE, BLACKLIST, WHITELIST, OUTPUT, EFFICIENCY_THRESHOLD


# item name -> drop rate
DropTable = Dict[str, float]
APCost = int
QuestInfo = Tuple[APCost, DropTable]
SectionInfo = Dict[str, QuestInfo]
# item name -> (APD, node name)
BestAPD = Dict[str, Tuple[float, str]]
# item name -> {node name -> APD}
DropLocationData = Dict[str, Dict[str, float]]
# location name, efficiency rating, specific item APD
LocationEfficiency = Tuple[str, float, float]


def output_json(object: Any, filename: str) -> None:
    with open(PATH_PREFIX + filename, 'w') as fo:
        json.dump(object, fo, indent='\t')


def check_include(itemname: str) -> bool:
    """ returns True if item should be included, False if not """
    if WHITELIST:
        if itemname not in WHITELIST:
            return False
    elif itemname in BLACKLIST:
        return False
    return True


def generate_node_name(section_name: str, quest_name: str) -> str:
    return section_name + " - " + quest_name


def get_material_apd_and_locations(drop_data: Dict[str, SectionInfo]) -> Tuple[BestAPD, DropLocationData]:
    best_APD: BestAPD = {}
    drop_locations: DropLocationData = {}

    for section_name, section_data in drop_data.items():
        for (quest_name, (ap, drops)) in section_data.items():
            node_name = generate_node_name(section_name, quest_name)
            for item_name, rate in drops.items():
                if not check_include(item_name):
                    continue

                apd = ap / rate
                if item_name not in best_APD or best_APD[item_name][0] > apd:
                    best_APD[item_name] = (apd, node_name)
                if item_name not in drop_locations:
                    drop_locations[item_name] = {}
                drop_locations[item_name][node_name] = apd
    return best_APD, drop_locations


def get_efficiency(drop_data: Dict[str, SectionInfo], best_APD: BestAPD) -> Dict[str, float]:
    efficiency: Dict[str, float] = {}

    for section_name, section_data in drop_data.items():
        for (quest_name, (ap, drops)) in section_data.items():
            node_name = generate_node_name(section_name, quest_name)
            total_ap_value = sum(
                best_APD[item_name][0] * rate
                for item_name, rate in drops.items()
                if check_include(item_name)
            )
            eff = total_ap_value / ap
            efficiency[node_name] = eff
    return efficiency


def main():
    with open(DROPS_FILE, "r") as fo:
        drop_data: Dict[str, SectionInfo] = json.load(fo)

    best_APD, drop_locations = get_material_apd_and_locations(drop_data)
    efficiency = get_efficiency(drop_data, best_APD)

    best_spot_by_item: Dict[str, LocationEfficiency] = {}
    locations_efficiency: Dict[str, List[LocationEfficiency]] = {}

    for iname, locs in drop_locations.items():
        # filter out efficiency < EFFICIENCY_THRESHOLD places
        effs = [(loc, efficiency[loc], apd)
                for loc, apd in locs.items()
                if efficiency[loc] >= EFFICIENCY_THRESHOLD]
        effs.sort(key=lambda x: x[1], reverse=True)

        best_spot_by_item[iname] = effs[0]
        locations_efficiency[iname] = effs

    output_json(best_APD, "apd.json")
    output_json(drop_locations, "locations.json")
    output_json(efficiency, "efficiency.json")
    output_json(best_spot_by_item, "best_locations.json")
    output_json(locations_efficiency, "locations_efficiency.json")

    longest = min(60, max(len(name) for item in OUTPUT for name in drop_locations[item].keys()))

    for item in OUTPUT:
        print("#", item)
        for (name, eff, apd) in locations_efficiency[item]:
            if len(name) > longest:
                name = name[:longest - 3] + "..."
            print("  {name:{length}.{length}s} -- {eff:4.2f} {apd:5.1f}".format(name=name, eff=eff, apd=apd, length=longest))


if __name__ == "__main__":
    main()
