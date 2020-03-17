import pickle
import os.path

from fast_randint import randint


CARD_DEFS_PICKLE_PATH = 'card_defs.pickle'
CARD_DEF_BOOL_FIELDS = (
    'DIVINE_SHIELD',
    'WINDFURY',
    'TAUNT',
    'POISONOUS',
    'REBORN',
    'DEATHRATTLE'
)


def save_card_defs():
    import xml.etree.ElementTree as ET
    tree = ET.parse('hsdata/CardDefs.xml')
    defs = {}

    for child in tree.getroot():
        card = {
            'ID': int(child.attrib['ID']),
            'CardID': child.attrib['CardID']
        }
        for tag in child:
            value = tag.attrib.get('value', None)
            if tag.attrib['name'] != value:
                if tag.attrib['type'] == 'Int':
                    if tag.attrib['name'] in CARD_DEF_BOOL_FIELDS:
                        value = bool(int(value))
                    else:
                        value = int(value)
                elif tag.attrib['type'] == 'LocString':
                    value = {s.tag: s.text for s in tag}['enUS']
                card[tag.attrib['name']] = value
        defs[card['CardID']] = card

    with open(CARD_DEFS_PICKLE_PATH, 'wb') as fh:
        pickle.dump(defs, fh)
    return defs

def load_card_defs():
    if not os.path.exists(CARD_DEFS_PICKLE_PATH):
        return save_card_defs()
    with open(CARD_DEFS_PICKLE_PATH, 'rb') as fh:
        return pickle.load(fh)

card_defs = load_card_defs()

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
