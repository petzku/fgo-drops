#!/usr/bin/env python3

"""
Get drop rate info from Gamepress.

Made for use with drop_efficiency.py, but should work for other stuff too
"""
from urllib.request import urlopen, Request
import html

# TODO: maybe parse properly instead of regex shit
import re

from typing import Dict, List, Tuple
from config import BASE_URL, DROPS_FILE

# type variables
DropTable = Dict[str, float]
APCost = int
QuestInfo = Tuple[APCost, DropTable]
SectionInfo = Dict[str, QuestInfo]

# parsing regexes
ap_regex = re.compile(r'>(\d+)<')
item_regex = re.compile(r'"en">([^<]+)</a> (?:x\d )?(?:([\d.]+)%)?')
location_regex = re.compile(r'<a[^<]+href="([^\"]*)"[^<]*>([^<]+)</a>')


def download_url(url: str) -> str:
    req = Request(BASE_URL + url, headers={'User-Agent': 'Mozilla/5.0'})
    pagetext = urlopen(req).read().decode('utf-8')
    pagetext = html.unescape(pagetext)
    return pagetext


def get_free_quests() -> Dict[str, List[Tuple[str, str]]]:
    pagetext = download_url('/free-quests')

    start_str = '<div class="view-grouping-header"><div id="1776"></div>'  # start of Fuyuki block
    end_str = '<div class="view-grouping-header"><div id="7616"></div>'    # start of LB3 block
    pagetext = start_str + pagetext.split(start_str)[1].split(end_str)[0]

    fqs: Dict[str, List[Tuple[str, str]]] = {}
    by_sections = pagetext.split('<div class="view-grouping-header">')

    quest_regex = re.compile(r'href="(.+?)".*?>([^<]+)')

    for section in by_sections:
        if not section:
            continue

        title_match = re.search(r'^[^<]+', section, re.MULTILINE)
        if not title_match:
            print("!! error, no title found in lines:")
            print('\n'.join('\t'+s for s in section.splitlines()[:3]))
            print()
            continue
        else:
            title = title_match.group(0)
            print("Found title: " + title)

        quests = []
        for line in section.splitlines():
            if "/quest/" in line:
                (url, name), = quest_regex.findall(line)
                url = url.replace('/grandorder', '')
                quests.append((name, url))
        fqs[title] = quests
    return fqs


def get_singularity(title: str, quests: List[Tuple[str, str]]) -> SectionInfo:
    location_filter_regex = re.compile(r'{:s} - (.+)'.format(title))
    ds: SectionInfo = {}

    for name, url in quests:
        droptable: DropTable = {}
        pagetext = download_url(url)

        quest_drops_text = pagetext.split("Quest Drops")[1].split("Quest Reward")[0]
        location_text = pagetext.split("<div id=\"main-quest\">")[1].split("AP Cost")[0]
        (lurl, lname), = location_regex.findall(location_text)
        namefilter_match = location_filter_regex.match(lname)
        if namefilter_match:
            lname = namefilter_match.group(1)

        ap_text: str = pagetext.split("AP Cost")[1].splitlines()[1]
        ap_cost: int = int(ap_regex.findall(ap_text)[0])

        for line in quest_drops_text.splitlines():
            if "/item/" in line and "</td>" in line:
                (iname, chance), = item_regex.findall(line)
                if not chance:
                    print("no drop rate listed! {:s} - {:s}: {:s}".format(title, name, iname))
                    print("on line:", repr(line))
                else:
                    droptable[iname] = float(chance)/100
        ds[lname + ": " + name] = (ap_cost, droptable)
    return ds


def export_drops(drops: Dict[str, SectionInfo]):
    with open(DROPS_FILE, 'w') as fo:
        import json
        print("exporting json...", end=" ")
        json.dump(drops, fo)
    print("done")


def main():
    # start by getting all free quests
    # TODO: possibly consider daily (material) quests too
    fqs = get_free_quests()

    for t, qs in fqs.items():
        print(t)
        print('\n'.join('\t%s (%s)' % (n, u) for (n, u) in qs))

    drops: Dict[str, SectionInfo] = {}

    for title, quests in fqs.items():
        if title.startswith("Lostbelt"):
            title = title.split(": ", 1)[1]
        print("starting:", title)

        ds = get_singularity(title, quests)

        drops[title] = ds
        print("done:", title)

    export_drops(drops)


if __name__ == "__main__":
    main()
