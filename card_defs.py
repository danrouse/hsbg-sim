import xml.etree.ElementTree as ET
from random import randint

tree = ET.parse('hsdata/CardDefs.xml')
card_defs = {}

for child in tree.getroot():
    card = {
        'ID': int(child.attrib['ID']),
        'CardID': child.attrib['CardID']
    }
    for tag in child:
        value = tag.attrib.get('value', None)
        if tag.attrib['name'] != value:
            if tag.attrib['type'] == 'Int':
                value = int(value)
            elif tag.attrib['type'] == 'LocString':
                value = {s.tag: s.text for s in tag}['enUS']
            card[tag.attrib['name']] = value
    card_defs[card['CardID']] = card


def get_random_card_id(
    ignore_id='',
    battlegrounds_only=True,
    battlegrounds_triple=False,
    cache={},
    **kwargs
):
    cache_key = ignore_id + str(kwargs) + str(battlegrounds_triple)
    matches = cache.get(cache_key, [])
    if not matches:
        for card in card_defs.values():
            if card.get('CardID') == ignore_id: continue
            if battlegrounds_only and not battlegrounds_triple and card.get('IS_BACON_POOL_MINION') != 1: continue
            if 'BaconUps' not in card.get('CardID') and battlegrounds_triple: continue
            match = False
            for key, val in kwargs.items():
                if card.get(key) == val:
                    match = True
                    break
            if match:
                matches.append(card.get('CardID'))
        cache[cache_key] = matches
    return matches[randint(0, len(matches) - 1)]
