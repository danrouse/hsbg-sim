import logging
from random import randint
from uuid import uuid4
from typing import List, Optional, Any

import hearthstone.enums

from entity import Entity
from card_effects import card_effects
from event import Event


# logging.basicConfig(level=logging.FATAL)
# logging.basicConfig(level=logging.DEBUG)


# TODO: Hero powers (How to detect if hero power active?)
#     Deathwing
#     Nefarian
#     Patches the Pirate
#     Ragnaros the Firelord
#     The Great Akazamarak (Secrets?)
# TODO: Passive minion buffs (are values are reported by Power.log buffed or unbuffed?)
# TODO (Code): Test examples
# TODO (Code): Linting
# TODO (Code): Docstrings
# TODO (Design): Board state visualizer

# Data collection: Annotate games, board minions and stats, whether hero powers are active in a combat


MAX_MINIONS = 7
CARD_ZAPP_SLYWICK = 'BGS_022'
CARD_ZAPP_SLYWICK_TRIPLE = 'TB_BaconUps_091'
CARD_BARON_RIVENDARE = 'FP1_031'
CARD_BARON_RIVENDARE_TRIPLE = 'TB_BaconUps_055'
CARD_KHADGAR = 'DAL_575'
CARD_KHADGAR_TRIPLE = 'TB_BaconUps_034'


class SimulatedCombat():
    def __init__(self, controllers):
        self.controllers = [
            [m.clone() for m in c]
            for c in controllers
        ]
        for i, c in enumerate(self.controllers):
            for minion in c:
                minion.controller_index = i
        self.logger = logging.getLogger('hsbg')
        self.turn_count = 0
        self.current_controller = self.get_first_controller()
        self.minion_deaths = [[], []]

    def debug_log(self, *args):
        # defer casting entities to strings for performance
        if self.logger.level >= logging.DEBUG:
            s = ':'.join([str(a) for a in args])
            self.logger.debug(s)
        # elif args[0] == 'trigger':
        #     print(':'.join([str(a) for a in args]))

    #
    # Entity Selectors
    #

    def get_all_minions(self):
        minions = self.controllers[self.current_controller] + \
            self.controllers[0 if self.current_controller == 1 else 1]
        return [m for m in minions if m.health > 0]

    def get_enemies(self, enemy_to: Entity, allow_dead: Optional[bool] = False):
        controller_index = self.get_entity_controller_index(enemy_to)
        minions = self.controllers[0 if controller_index == 1 else 1]
        return [m for m in minions if allow_dead or m.health > 0]

    def get_random_enemy(self, enemy_to: Entity):
        enemies = self.get_enemies(enemy_to)
        if not enemies: return []
        return enemies[randint(0, len(enemies) - 1)]

    def get_friendlies(self, friendly_to: Entity, ignore_self=False, **kwargs):
        controller_index = self.get_entity_controller_index(friendly_to)
        friendlies = [
            m for m in self.controllers[controller_index]
            if m.health > 0 and (not ignore_self or (ignore_self and m.id != friendly_to.id))
        ]
        if not kwargs: return friendlies
        matches = []
        for ent in friendlies:
            match = True
            for key, val in kwargs.items():
                if getattr(ent, key) != val:
                    match = False
                    break
            if match:
                matches.append(ent)
        return matches

    def get_random_friendly(self, friendly_to: Entity, ignore_self=True, **kwargs):
        friendlies = self.get_friendlies(friendly_to, ignore_self=ignore_self, **kwargs)
        if not friendlies: return
        return friendlies[randint(0, len(friendlies) - 1)]

    def get_first_two_friendly_mechs_that_died(self, friendly_to: Entity):
        controller_index = self.get_entity_controller_index(friendly_to)
        dead_minions = self.minion_deaths[controller_index]
        dead_mechs = [m for m in dead_minions if m.race == hearthstone.enums.Race.MECHANICAL]
        return dead_mechs[:2]

    #
    # Game/board state calculation
    #

    def get_first_controller(self):
        if len(self.controllers[0]) != len(self.controllers[1]):
            minion_counts = [len(i) for i in self.controllers]
            return minion_counts.index(max(minion_counts))
        return randint(0, 1)

    def get_winner(self):
        if not self.controllers[0] and not self.controllers[1]:
            return (-1, 0)
        elif not self.controllers[0]:
            damage = sum([int(m.tier) for m in self.controllers[1]])
            return (1, damage)
        elif not self.controllers[1]:
            damage = sum([int(m.tier) for m in self.controllers[0]])
            return (0, damage)

    def get_next_attacker(self, controller_index: int):
        for minion in self.controllers[controller_index]:
            if not minion.exhausted and minion.attack:
                return minion
        # reset exhausted if no eligible minions found
        for minion in self.controllers[controller_index]:
            minion.exhausted = False
        for minion in self.controllers[controller_index]:
            if minion.attack:
                return minion

    def get_eligible_defender(self, controller_index: int, lowest_health: bool = False):
        defenders = self.controllers[controller_index]
        if not defenders: return
        if lowest_health:
            min_health = min([d.health for d in defenders])
            defenders = [d for d in defenders if d.health == min_health]
        else:
            taunt_defenders = [d for d in defenders if d.taunt]
            if taunt_defenders:
                defenders = taunt_defenders
        return defenders[randint(0, len(defenders) - 1)]

    def get_baron_rivendare_deathrattle_multiplier(self, entity: Entity):
        multiplier = 1
        for entity in self.get_friendlies(entity):
            if entity.card_id == CARD_BARON_RIVENDARE:
                multiplier = max(2, multiplier)
            elif entity.card_id == CARD_BARON_RIVENDARE_TRIPLE:
                multiplier = max(3, multiplier)
        return multiplier

    def get_khadgar_summon_multiplier(self, entity: Entity):
        multiplier = 1
        for entity in self.get_friendlies(entity):
            if entity.card_id == CARD_KHADGAR:
                multiplier = max(2, multiplier)
            elif entity.card_id == CARD_KHADGAR_TRIPLE:
                multiplier = max(3, multiplier)
        return multiplier

    def get_entity_controller_index(self, entity: Entity):
        if entity.controller_index is not None:
            return entity.controller_index
        for i, c in enumerate(self.controllers):
            for m in c:
                if m.id == entity.id:
                    return i
        raise Exception('No controller index found')

    def get_entity_index(self, entity: Entity):
        return self.controllers[self.get_entity_controller_index(entity)].index(entity)

    #
    # Actions
    #

    def handle_entity_death(self, entity: Entity):
        if entity.deathrattle:
            for _ in range(self.get_baron_rivendare_deathrattle_multiplier(entity)):
                deathrattle_triggered = self.trigger(entity, Event.DEATHRATTLE)
                for ench_card_id in entity.enchantments:
                    ench_trigger_deathrattle = card_effects.get(ench_card_id, {}).get('enchantment_of')
                    if ench_trigger_deathrattle:
                        ench_triggered = self.trigger(entity, Event.DEATHRATTLE, trigger_from_card=ench_trigger_deathrattle)
                        deathrattle_triggered = deathrattle_triggered or ench_triggered
            if not deathrattle_triggered:
                self.logger.warning(f'damage:unknown_deathrattle:{entity}, {entity.enchantments}')

        for minion in self.get_all_minions():
            if minion is not entity:
                self.trigger(minion, Event.MINION_DIED, entity)

        self.debug_log('damage', 'death', entity)

        # TODO: Is reborn before or after friendly death effects?
        if entity.reborn:
            self.debug_log('damage', 'reborn', entity)
            self.summon(entity, entity.card_id, reborn=False)
        else:
            controller_index = self.get_entity_controller_index(entity)
            self.minion_deaths[controller_index].append(entity)

    def clean_up_dead_minions(self):
        for c_i, c in enumerate(self.controllers):
            self.controllers[c_i] = [m for m in c if m.health > 0]

    def trigger(
        self,
        entity: Entity,
        trigger_name: Event,
        *args: List[Any],
        trigger_from_card: Optional[str] = None,
    ):
        impl = card_effects.get(trigger_from_card) if trigger_from_card else entity.effects
        if trigger_name in impl:
            self.debug_log('trigger', trigger_name, entity)
            impl[trigger_name](self, entity, *args)
            return True
        elif 'triple_of' in impl:
            impl = card_effects.get(impl['triple_of'], {})
            if trigger_name in impl:
                self.debug_log('trigger', trigger_name, entity)
                for _ in range(2):
                    impl[trigger_name](self, entity, *args)
                return True

    def summon(
        self,
        entity: Entity,
        card_id: str,
        index: Optional[int] = None,
        count: int = 1,
        **kwargs
    ):
        m_id = self.get_entity_index(entity)
        index = index or m_id
        new_entity = None
        controller_index = self.get_entity_controller_index(entity)

        for _ in range(count * self.get_khadgar_summon_multiplier(entity)):
            if len([m for m in self.controllers[controller_index] if m.health > 0]) == MAX_MINIONS:
                self.debug_log('summon', index, 'failed, board is full', entity.name)
                return

            new_entity = Entity(id=uuid4(), card_id=card_id, controller_index=controller_index, **kwargs)
            self.debug_log('summon', index, new_entity)
            self.controllers[controller_index].insert(index, new_entity)

            for entity in self.controllers[controller_index]:
                if entity is not new_entity:
                    self.trigger(entity, Event.FRIENDLY_MINION_SUMMONED, new_entity)

        return new_entity

    def buff(
        self,
        entities: List[Entity],
        attack: int = 0,
        health: int = 0,
        divine_shield: Optional[bool] = None,
        taunt: Optional[bool] = None
    ):
        for entity in entities:
            entity.attack += attack
            entity.health += health
            if divine_shield is not None:
                entity.divine_shield = divine_shield
            if taunt is not None:
                entity.taunt = taunt
            self.debug_log('buff', entity, attack, health, divine_shield, taunt)

    def damage(
        self,
        entities: List[Entity],
        attacker: Entity,
        damage: Optional[int] = None,
        poisonous: Optional[bool] = None
    ):
        if damage is None: damage = attacker.attack
        if poisonous is None: poisonous = attacker.poisonous
        for entity in entities:
            minion_index = self.get_entity_index(entity)

            if entity.divine_shield:
                entity.divine_shield = False
                self.debug_log('damage', 'divine_shield_lost', entity)
                for minion in self.get_friendlies(entity):
                    if minion is not entity:
                        self.trigger(minion, Event.FRIENDLY_MINION_LOST_DIVINE_SHIELD, entity)
            else:
                entity.health -= damage
                self.trigger(entity, Event.DAMAGE_RECEIVED, minion_index)

                if poisonous and entity.health > 0:
                    entity.health = 0
                if entity.health <= 0:
                    self.handle_entity_death(entity)
                if entity.health < 0:
                    self.trigger(entity, Event.OVERKILL)

    #
    # Attacking/Turn order
    #

    def attack_with(self, attacker: Entity):
        attacker_controller_index = self.get_entity_controller_index(attacker)
        enemy_controller_index = int(not attacker_controller_index)
        defender = self.get_eligible_defender(enemy_controller_index, lowest_health=attacker.card_id in [CARD_ZAPP_SLYWICK, CARD_ZAPP_SLYWICK_TRIPLE])
        if not defender: return

        self.trigger(attacker, Event.BEFORE_ATTACK)

        defender_index = self.get_entity_index(defender)
        defender_controller_index = self.get_entity_controller_index(defender)
        cleave_targets = []
        if defender_index > 0:
            cleave_targets.append(self.controllers[defender_controller_index][defender_index - 1])
        if defender_index < len(self.controllers[defender_controller_index]) - 1:
            cleave_targets.append(self.controllers[defender_controller_index][defender_index + 1])

        self.debug_log('attack', attacker, defender)
        self.damage([defender], attacker)
        self.damage([attacker], defender)

        if attacker.cleave:
            for target in cleave_targets:
                self.debug_log('attack', 'cleave', attacker, target)
                self.damage([target], attacker)

        self.clean_up_dead_minions()

    def handle_turn(self, controller_index: int, single_turn=False):
        self.turn_count += 1
        self.debug_log('turn', self.turn_count)
        if self.turn_count == 1:
            for entity in self.get_all_minions():
                self.trigger(entity, Event.COMBAT_START)
        self.current_controller = controller_index
        enemy_controller_index = int(not controller_index)

        if self.get_winner(): return self.get_winner()

        attacker = self.get_next_attacker(controller_index)
        if not attacker:
            # check that next player has a valid attack, or stalemate
            if not self.get_next_attacker(enemy_controller_index):
                return (-1, 0)
            return self.handle_turn(enemy_controller_index)

        self.attack_with(attacker)
        if attacker.windfury and attacker.health > 0:
            self.attack_with(attacker)
            if (
                attacker.card_id == CARD_ZAPP_SLYWICK_TRIPLE and
                attacker.health > 0
            ):
                self.attack_with(attacker)

        attacker.exhausted = True

        if single_turn: return
        return self.handle_turn(enemy_controller_index)

    def simulate(self):
        return self.handle_turn(self.current_controller)
