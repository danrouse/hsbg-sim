import re
import time

from card_defs import card_defs
from entity import Entity
from simulate import SimulatedCombat
from chart import plot_probabilities


def parse_entity_id(entity: str):
    if entity.startswith('['):
        match = re.match(r'\[entityName=(.+) id=(\d+) zone=(\w+) zonePos=(\d+) cardId=(\w*) player=(\d+)', entity)
        return match.group(2)
    return entity


class Parser():
    def __init__(self):
        self.entities = {}
        self.games = []
        self.cur_entity = None

    def get_game_state(self):
        controllers = {}
        has_bob = bool([s for s in self.entities.values() if s.get('card_id') == 'TB_BaconShopBob' and s.get('ZONE') == 'PLAY'])
        if has_bob: return []
        for id, ent in self.entities.items():
            card_id = ent.get('card_id')
            card_type = ent.get('CARDTYPE')
            controller = ent.get('CONTROLLER')
            attack = int(ent.get('ATK', 0))
            health = int(ent.get('HEALTH', 0))
            if card_type in ['MINION', 'HERO', 'ENCHANTMENT'] and ent.get('ZONE') not in ['REMOVEDFROMGAME', 'GRAVEYARD', 'SETASIDE']:
                if controller not in controllers:
                    controllers[controller] = {
                        'HERO': None,
                        'MINION': []
                    }
                if card_type == 'HERO':
                    controllers[controller][card_type] = ent
                elif card_type == 'ENCHANTMENT':
                    for minion in controllers[controller]['MINION']:
                        if minion and minion.id == ent.get('ATTACHED'):
                            minion.enchantments.append(card_id)
                else:
                    while len(controllers[controller][card_type]) < int(ent.get('ZONE_POSITION')):
                        controllers[controller][card_type].append(None)
                    controllers[controller][card_type][int(ent.get('ZONE_POSITION')) - 1] = Entity(
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
        return [s for s in controllers.values()]

    def predict_outcome(self, controllers, heroes, n=1000):
        outcomes = []
        times = []
        for i in range(n):
            t_a = time.time()
            winner, damage = SimulatedCombat([c['MINION'] for c in controllers]).simulate()
            t_b = time.time()
            times.append(t_b - t_a)
            if winner != -1:
                damage += int(controllers[winner]['HERO']['PLAYER_TECH_LEVEL'])
            if winner == 1:
                damage *= -1

            outcomes.append(damage)

        prob_win = len([k for k in outcomes if k > 0]) / n
        prob_loss = len([k for k in outcomes if k < 0]) / n
        prob_draw = len([k for k in outcomes if k == 0]) / n

        print(f'Avg time: {sum(times) / n}')
        print(f'Total time: {sum(times)}')
        print(f'Win: {prob_win}')
        print(f'Loss: {prob_loss}')
        print(f'Draw: {prob_draw}')

        plot_probabilities(outcomes, heroes)

    def dump_game(self):
        has_heroes = True
        controllers = self.get_game_state()
        if len(controllers) != 2: return
        heroes = []  # TODO: clean up hero handling/passing into SimulatedCombat
        for controller in controllers:
            if not controller.get('HERO'):
                has_heroes = False
                break
            hero = (controller or {}).get('HERO', {}) or {}
            tier = hero.get('PLAYER_TECH_LEVEL', '?')
            hero_card_id = hero.get('card_id')
            hero_name = hero.get('card', {}).get('CARDNAME', 'Unknown Hero')
            hero_hp = int(hero.get('HEALTH', 40)) - int(hero.get('DAMAGE', 0))
            heroes.append((hero_card_id, hero_name, hero_hp))
            print(f'{hero_name} ({tier}) {hero_hp} HP')
            for minion in controller['MINION']:
                print('\t', minion)

        if has_heroes:
            print('-----------------------------------')
            print(self.predict_outcome(controllers, heroes))
            print('===================================')

    def update_entity(self, entity, tag, value):
        entity_id = parse_entity_id(entity)
        if entity_id not in self.entities:
            self.entities[entity_id] = {}
        self.entities[entity_id][tag] = value

        if entity_id == 'GameEntity' and tag == 'STEP' and value == 'MAIN_READY':
            self.dump_game()

    def handle_log_line(self, line):
        if 'GameState.DebugPrintPower()' in line:
            if 'CREATE_GAME' in line:
                if self.entities: self.games.append(self.entities)
                self.entities = {}
            elif 'FULL_ENTITY' in line:
                match = re.search(r'FULL_ENTITY - Creating ID=(?P<id>\d+) CardID=(?P<card_id>\w*)', line)
                self.cur_entity = match.group('id')
                self.entities[self.cur_entity] = {
                    'card_id': match.group('card_id').strip(),
                    'card': card_defs.get(match.group('card_id').strip())
                }
            elif 'SHOW_ENTITY' in line:
                match = re.search(r'SHOW_ENTITY - Updating Entity=(?P<id>.+) CardID=(?P<card_id>\w*)', line)
                self.cur_entity = parse_entity_id(match.group('id'))
                self.entities[self.cur_entity]['card_id'] = match.group('card_id').strip()
                self.entities[self.cur_entity]['card'] = card_defs.get(match.group('card_id').strip())
            elif 'TAG_CHANGE' in line:
                match = re.search(r'TAG_CHANGE Entity=(?P<id>.+) tag=(?P<tag>.+) value=(?P<value>.+)', line)
                self.update_entity(match.group('id'), match.group('tag'), match.group('value').strip())
            elif self.cur_entity:
                match = re.search(r'tag=(?P<tag>.+) value=(?P<value>.+)', line)
                if match:
                    self.update_entity(self.cur_entity, match.group('tag'), match.group('value').strip())
                else:
                    self.cur_entity = None

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
