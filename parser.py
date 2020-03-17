import re
import time

from card_defs import card_defs
from entity import Entity
from simulate import SimulatedCombat
# from chart import plot_probabilities


def parse_entity_id(entity: str):
    if entity.startswith('['):
        match = re.match(r'\[entityName=(.+) id=(\d+) zone=(\w+) zonePos=(\d+) cardId=(\w*) player=(\d+)', entity)
        return match.group(2)
    return entity


class Parser():
    def __init__(self):
        self.entity_defs = {}
        self.games = []
        self.cur_entity_id = None

    def get_game_state(self):
        heroes = {}
        minions = {}
        has_bob = bool([s for s in self.entity_defs.values() if s.get('card_id') == 'TB_BaconShopBob' and s.get('ZONE') == 'PLAY'])
        if has_bob: return []
        for id, ent in self.entity_defs.items():
            card_id = ent.get('card_id')
            card_type = ent.get('CARDTYPE')
            controller = ent.get('CONTROLLER')
            attack = int(ent.get('ATK', 0))
            health = int(ent.get('HEALTH', 0))
            if card_type in ['MINION', 'HERO', 'ENCHANTMENT'] and ent.get('ZONE') not in ['REMOVEDFROMGAME', 'GRAVEYARD', 'SETASIDE']:
                if card_type == 'HERO':
                    heroes[controller] = Entity(
                        id=controller,
                        card_id=card_id,
                        health=health - int(ent.get('DAMAGE', 0)),
                        tier=int(ent.get('PLAYER_TECH_LEVEL', 1))
                    )
                elif card_type == 'ENCHANTMENT':
                    for minion in minions[controller]:
                        if minion and minion.id == ent.get('ATTACHED'):
                            minion.enchantments.append(card_id)
                else:
                    if controller not in minions:
                        minions[controller] = []
                    while len(minions[controller]) < int(ent.get('ZONE_POSITION')):
                        minions[controller].append(None)
                    minions[controller][int(ent.get('ZONE_POSITION')) - 1] = Entity(
                        id=id,
                        card_id=card_id,
                        attack=attack,
                        health=health,
                        divine_shield=bool(int(ent.get('DIVINE_SHIELD', 0))),
                        windfury=bool(int(ent.get('WINDFURY', 0))),
                        taunt=bool(int(ent.get('TAUNT', 0))),
                        poisonous=bool(int(ent.get('POISONOUS', 0))),
                        reborn=bool(int(ent.get('REBORN', 0))),
                        deathrattle=bool(int(ent.get('DEATHRATTLE', 0)))
                    )
        return list(zip(heroes.values(), minions.values()))

    def handle_turn_start(self):
        players = self.get_game_state()
        if len(players) != 2: return

        for hero, minions in players:
            print(f"{hero.name} ({hero.tier}) {hero.health} HP")
            for minion in minions:
                print('\t', minion)

        print('-----------------------------------')
        outcomes = SimulatedCombat.predict_outcome(players)
        prob_win = sum([v for k,v in outcomes if k > 0])
        prob_loss = sum([v for k,v in outcomes if k < 0])
        prob_draw = sum([v for k,v in outcomes if k == 0])
        print(f'Win: {round(prob_win * 100, 2)}%')
        print(f'Loss: {round(prob_loss * 100, 2)}%')
        print(f'Draw: {round(prob_draw * 100, 2)}%')
        print('===================================')

    def update_entity(self, entity, tag, value):
        entity_id = parse_entity_id(entity)
        if entity_id not in self.entity_defs:
            self.entity_defs[entity_id] = {}
        self.entity_defs[entity_id][tag] = value

        if entity_id == 'GameEntity' and tag == 'STEP' and value == 'MAIN_READY':
            self.handle_turn_start()

    def handle_log_line(self, line):
        if 'GameState.DebugPrintPower()' in line:
            if 'CREATE_GAME' in line:
                if self.entity_defs: self.games.append(self.entity_defs)
                self.entity_defs = {}
            elif 'FULL_ENTITY' in line:
                match = re.search(r'FULL_ENTITY - Creating ID=(?P<id>\d+) CardID=(?P<card_id>\w*)', line)
                self.cur_entity_id = match.group('id')
                self.entity_defs[self.cur_entity_id] = {
                    'card_id': match.group('card_id').strip(),
                    'card': card_defs.get(match.group('card_id').strip())
                }
            elif 'SHOW_ENTITY' in line:
                match = re.search(r'SHOW_ENTITY - Updating Entity=(?P<id>.+) CardID=(?P<card_id>\w*)', line)
                self.cur_entity_id = parse_entity_id(match.group('id'))
                self.entity_defs[self.cur_entity_id]['card_id'] = match.group('card_id').strip()
                self.entity_defs[self.cur_entity_id]['card'] = card_defs.get(match.group('card_id').strip())
            elif 'TAG_CHANGE' in line:
                match = re.search(r'TAG_CHANGE Entity=(?P<id>.+) tag=(?P<tag>.+) value=(?P<value>.+)', line)
                self.update_entity(match.group('id'), match.group('tag'), match.group('value').strip())
            elif self.cur_entity_id:
                match = re.search(r'tag=(?P<tag>.+) value=(?P<value>.+)', line)
                if match:
                    self.update_entity(self.cur_entity_id, match.group('tag'), match.group('value').strip())
                else:
                    self.cur_entity_id = None

    def parse_games(self, path: str, last=True):
        with open(path, 'r') as fh:
            if last:
                last_game_start = 0
                while True:
                    line = fh.readline()
                    if not line: break
                    if 'CREATE_GAME' in line:
                        last_game_start = fh.tell()
                fh.seek(last_game_start)
            while True:
                line = fh.readline()
                if not line: break
                self.handle_log_line(line)
