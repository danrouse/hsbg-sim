import unittest
import unittest.mock
from random import randint
import hearthstone.enums

from card_defs import get_random_card_id
from entity import Entity
from simulate import SimulatedCombat, MAX_MINIONS
from event import Event


def create_entity(card_name: str = 'Mechano-Egg', triple=False, **kwargs):
    return Entity(get_random_card_id(battlegrounds_triple=triple, CARDNAME=card_name), **kwargs)


def create_entities(defs):
    return [create_entity(*d) for d in defs]


class TestSimulatedCombat(unittest.TestCase):
    def test_get_all_minions_count(self):
        minion_counts = [randint(1, 7), randint(1, 7)]
        combat = SimulatedCombat((
            [create_entity() for _ in range(minion_counts[0])],
            [create_entity() for _ in range(minion_counts[1])]
        ))
        self.assertEqual(len(combat.get_all_minions()), sum(minion_counts))

    def test_get_enemies(self):
        friendly = create_entity()
        enemies = [create_entity() for _ in range(randint(1, 7))]
        combat = SimulatedCombat(([friendly], enemies))
        self.assertEqual(
            combat.get_enemies(friendly),
            enemies
        )

    def test_get_random_enemy_skips_dead(self):
        friendly = create_entity()
        living_enemy = create_entity()
        dead_enemy = create_entity(health=0)
        combat = SimulatedCombat(([friendly], [living_enemy, dead_enemy]))
        self.assertEqual(
            combat.get_random_enemy(friendly),
            living_enemy
        )

    def test_get_friendlies(self):
        source = create_entity()
        friendly = create_entity()
        combat = SimulatedCombat(([source, friendly], [create_entity()]))
        self.assertEqual(
            combat.get_friendlies(source),
            [source, friendly]
        )

    def test_get_friendlies_filter_race(self):
        source = create_entity()
        friendly_neutral = create_entity()
        friendly_demon = create_entity('Voidlord')
        combat = SimulatedCombat((
            [source, friendly_neutral, friendly_demon],
            [create_entity()]
        ))
        self.assertEqual(
            combat.get_friendlies(source, race=hearthstone.enums.Race.DEMON),
            [friendly_demon]
        )

    def test_get_random_friendly_ignores_self(self):
        source = create_entity()
        friendly = create_entity()
        combat = SimulatedCombat((
            [source, friendly],
            [create_entity()]
        ))
        self.assertEqual(
            combat.get_random_friendly(source, ignore_self=True),
            friendly
        )

    def test_get_first_controller_more_minions(self):
        bigger = [create_entity() for _ in range(2)]
        smaller = [create_entity()]
        combat_a = SimulatedCombat((bigger, smaller))
        combat_b = SimulatedCombat((smaller, bigger))
        self.assertEqual(combat_a.current_controller, 0)
        self.assertEqual(combat_b.current_controller, 1)

    def test_get_winner(self):
        loser = []
        minion = create_entity(health=1)
        winner = [minion]
        combat = SimulatedCombat((loser, winner))
        self.assertEqual(combat.get_winner(), (1, minion.tier))

    def test_get_winner_draw(self):
        combat = SimulatedCombat(([], []))
        self.assertEqual(combat.get_winner(), (-1, 0))

    def test_get_next_attacker_skip_zero_attack(self):
        zero_attack_minion = create_entity(attack=0)
        next_minion = create_entity(attack=1)
        combat = SimulatedCombat(([zero_attack_minion, next_minion], []))
        self.assertEqual(combat.get_next_attacker(0), next_minion)

    def test_get_eligible_defender_taunt(self):
        taunted_enemy = create_entity(taunt=True)
        untaunted_enemy = create_entity(taunt=False)
        attacker = create_entity(attack=1)
        combat = SimulatedCombat((
            [untaunted_enemy, taunted_enemy],
            [attacker]
        ))
        result = combat.get_eligible_defender(0)
        self.assertEqual(result, taunted_enemy)

    def test_get_eligible_defender_zapp_lowest_health(self):
        lowest_health_enemy = create_entity(health=1)
        combat = SimulatedCombat((
            [
                create_entity(health=2),
                create_entity(health=3),
                create_entity(health=4),
                lowest_health_enemy
            ],
            [create_entity(attack=1)]
        ))
        result = combat.get_eligible_defender(0, lowest_health=True)
        self.assertEqual(result, lowest_health_enemy)

    @unittest.mock.patch('simulate.SimulatedCombat.trigger')
    def test_handle_entity_death_trigger_deathrattle(self, trigger):
        minion = create_entity(deathrattle=True)
        combat = SimulatedCombat(([minion], []))
        combat.handle_entity_death(minion)
        trigger.assert_any_call(minion, Event.DEATHRATTLE)
        trigger.reset_mock()

        combat.controllers[0].append(create_entity('Baron Rivendare'))
        combat.handle_entity_death(minion)
        trigger.assert_has_calls((
            unittest.mock.call(minion, Event.DEATHRATTLE),
            unittest.mock.call(minion, Event.DEATHRATTLE)
        ))
        trigger.reset_mock()

        del combat.controllers[0][-1]
        combat.controllers[0].append(create_entity('Baron Rivendare', triple=True))
        combat.handle_entity_death(minion)
        trigger.assert_has_calls((
            unittest.mock.call(minion, Event.DEATHRATTLE),
            unittest.mock.call(minion, Event.DEATHRATTLE),
            unittest.mock.call(minion, Event.DEATHRATTLE)
        ))

    def test_handle_entity_death_trigger_reborn(self):
        friendly = create_entity(deathrattle=False, reborn=True)
        combat = SimulatedCombat(([friendly], []))
        # combat.handle_entity_death(friendly)
        combat.damage([combat.controllers[0][0]], friendly, friendly.health)
        combat.clean_up_dead_minions()
        self.assertEqual(len(combat.controllers[0]), 1)
        self.assertEqual(combat.controllers[0][0].reborn, False)

    def test_summon_single(self):
        friendly = create_entity()
        combat = SimulatedCombat(([friendly], [create_entity()]))
        combat.summon(combat.controllers[0][0], get_random_card_id(CARDNAME='Kaboom Bot'))
        self.assertEqual(len(combat.controllers[0]), 2)

    def test_summon_multiple(self):
        friendly = create_entity()
        combat = SimulatedCombat(([friendly], [create_entity()]))
        combat.summon(combat.controllers[0][0], get_random_card_id(CARDNAME='Kaboom Bot'), count=4)
        self.assertEqual(len(combat.controllers[0]), 5)

    def test_summon_full_board_fails(self):
        friendlies = [create_entity() for _ in range(MAX_MINIONS)]
        combat = SimulatedCombat((friendlies, [create_entity()]))
        self.assertEqual(len(combat.controllers[0]), MAX_MINIONS)
        combat.summon(combat.controllers[0][0], get_random_card_id(CARDNAME='Kaboom Bot'))
        self.assertEqual(len(combat.controllers[0]), MAX_MINIONS)

    def test_summon_with_khadgar(self):
        khadgar = create_entity('Khadgar')
        combat = SimulatedCombat(([khadgar], []))
        combat.summon(combat.controllers[0][0], get_random_card_id(CARDNAME='Kaboom Bot'))
        self.assertEqual(len(combat.controllers[0]), 3)

        triple_khadgar = create_entity('Khadgar', triple=True)
        combat.controllers[0] = [triple_khadgar]
        self.assertEqual(len(combat.controllers[0]), 1)
        combat.summon(combat.controllers[0][0], get_random_card_id(CARDNAME='Kaboom Bot'))
        self.assertEqual(len(combat.controllers[0]), 4)

    def test_damage_simple(self):
        attacker = create_entity(attack=1)
        defender = create_entity(health=2)
        combat = SimulatedCombat(([attacker], [defender]))
        combat.damage([defender], attacker)
        self.assertEqual(defender.health, 1)

    def test_damage_poisonous(self):
        attacker = create_entity(attack=1, poisonous=True)
        defender = create_entity(health=2)
        combat = SimulatedCombat(([attacker], [defender]))
        combat.damage([defender], attacker)
        self.assertEqual(defender.health, 0)

    def test_damage_divine_shield(self):
        attacker = create_entity(attack=1)
        defender = create_entity(health=2, divine_shield=True)
        combat = SimulatedCombat(([attacker], [defender]))
        combat.damage([defender], attacker)
        self.assertEqual(defender.health, 2)
        self.assertEqual(defender.divine_shield, False)

    def test_handle_turn_stalemate(self):
        combat = SimulatedCombat((
            [create_entity(attack=0)],
            [create_entity(attack=0)]
        ))
        self.assertEqual(combat.handle_turn(0), (-1, 0))
        self.assertEqual(combat.handle_turn(1), (-1, 0))

    def test_clean_up_dead_minions(self):
        combat = SimulatedCombat((
            [create_entity(health=0), create_entity(health=-1), create_entity(health=1)],
            [create_entity(health=0), create_entity(health=-1)]
        ))
        combat.clean_up_dead_minions()
        self.assertEqual(len(combat.controllers[0]), 1)
        self.assertEqual(len(combat.controllers[1]), 0)

    @unittest.mock.patch('simulate.SimulatedCombat.attack_with')
    def test_handle_turn_windfury(self, attack_with):
        attacker = create_entity(attack=1, windfury=True)
        defender = create_entity(attack=0, health=100)
        combat = SimulatedCombat(([attacker], [defender]))
        combat.handle_turn(0, single_turn=True)
        attack_with.assert_has_calls((
            unittest.mock.call(attacker),
            unittest.mock.call(attacker)
        ))
        self.assertEqual(attack_with.call_count, 2)

    @unittest.mock.patch('simulate.SimulatedCombat.attack_with')
    def test_handle_turn_zapp_mega_windfury(self, attack_with):
        attacker = create_entity('Zapp Slywick', triple=True, attack=1, windfury=True)
        defender = create_entity(attack=0, health=100)
        combat = SimulatedCombat(([attacker], [defender]))
        combat.handle_turn(0, single_turn=True)
        attack_with.assert_has_calls((
            unittest.mock.call(attacker),
            unittest.mock.call(attacker),
            unittest.mock.call(attacker)
        ))
        self.assertEqual(attack_with.call_count, 3)

    # untested methods:
    #   get_first_two_friendly_mechs_that_died (NYI)
    #   simulate
    #   general handle_entity_death
    #   general trigger?
    #   general buff?
    #   general attack_with


if __name__ == '__main__':
    unittest.main()
