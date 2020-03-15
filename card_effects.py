import hearthstone.enums

from card_defs import get_random_card_id
from event import Event


card_effects = {
    #
    # Tier 1
    #

    # # Dire Wolf Alpha
    # 'EX1_162': {
    #     passive attack to adjacent minions (+1/+2)
    # },
    # 'TB_BaconUps_088': {'triple_of': 'EX1_162'},

    # Red Whelp
    'BGS_019': {
        Event.COMBAT_START: lambda g, minion: \
            g.damage([g.get_random_enemy(minion)], minion, damage=len(g.get_friendlies(minion, race=hearthstone.enums.Race.DRAGON)))
    },
    'TB_BaconUps_102': {'triple_of': 'BGS_019'},

    # Fiendish Servant
    'YOD_026': {
        Event.DEATHRATTLE: lambda g, minion: g.buff([g.get_random_friendly(minion)], minion.attack)
    },
    'TB_BaconUps_112': {'triple_of': 'YOD_026'},

    # Mecharoo
    'BOT_445': {
        Event.DEATHRATTLE: lambda g, minion: g.summon(minion, 'BOT_445t')
    },
    'TB_BaconUps_002': {
        'triple_of': 'BOT_445',
        Event.DEATHRATTLE: lambda g, minion: g.summon(minion, 'TB_BaconUps_002t')
    },

    # Selfless Hero
    'OG_221': {
        Event.DEATHRATTLE: lambda g, minion: \
            g.buff(g.get_random_friendly([minion], divine_shield=False), divine_shield=True)
    },
    'TB_BaconUps_014': {'triple_of': 'OG_221'},


    #
    # Tier 2
    #

    # # Murloc Warleader
    # 'EX1_507': {
    #     passive: your other murlocs have +2 attack
    # },
    # 'TB_BaconUps_008': {'triple_of': 'EX1_507'},

    # # Old Murk-Eye
    # 'EX1_062': {
    #     Passive: Has +1 Attack for each other Murloc on the field
    # },
    # 'TB_BaconUps_036': {'triple_of': 'EX1_062'},

    # # Waxrider Togwaggle
    # 'BGS_035': {
    #     Passive: Whenever a friendly Dragon kills an enemy, gain +2/+2
    # },
    # 'TB_BaconUps_105': {'triple_of': 'BGS_035'},

    # Glyph Guardian
    'TRLA_131': {
        Event.BEFORE_ATTACK: lambda g, minion: g.buff([minion], minion.attack)
    },
    'TB_BaconUps_115': {'triple_of': 'TRLA_131'},

    # Harvest Golem
    'EX1_556': {
        Event.DEATHRATTLE: lambda g, minion: g.summon(minion, 'skele21')
    },
    'TB_BaconUps_006': {
        'triple_of': 'EX1_556',
        Event.DEATHRATTLE: lambda g, minion: g.summon(minion, 'TB_BaconUps_006t')
    },

    # Imprisoner
    'BGS_014': {
        Event.DEATHRATTLE: lambda g, minion: g.summon(minion, 'BRM_006t')
    },
    'TB_BaconUps_113': {
        'triple_of': 'BGS_014',
        Event.DEATHRATTLE: lambda g, minion: g.summon(minion, 'TB_BaconUps_030t')
    },

    # Kaboom Bot
    'BOT_606': {
        Event.DEATHRATTLE: lambda g, minion: g.damage([g.get_random_enemy(minion)], minion, damage=4)
    },
    'TB_BaconUps_028': {'triple_of': 'BOT_606'},

    # Kindly Grandmother
    'KAR_005': {
        Event.DEATHRATTLE: lambda g, minion: g.summon(minion, 'KAR_005a')
    },
    'TB_BaconUps_004': {
        'triple_of': 'KAR_005',
        Event.DEATHRATTLE: lambda g, minion: g.summon(minion, 'TB_BaconUps_004t')
    },

    # Rat Pack
    'CFM_316': {
        Event.DEATHRATTLE: lambda g, minion: [
            g.summon(minion, 'CFM_316t') for i in range(minion.attack)
        ]
    },
    'TB_BaconUps_027': {
        'triple_of': 'CFM_316',
        Event.DEATHRATTLE: lambda g, minion: [
            g.summon(minion, 'TB_BaconUps_027t') for i in range(minion.attack)
        ]
    },

    # Scavenging Hyena
    'EX1_531': {
        Event.MINION_DIED: lambda g, minion, target: \
            g.buff([minion], 2, 1) if (
                target.race == hearthstone.enums.Race.BEAST and
                target.controller_index == minion.controller_index
            ) else 0
    },
    'TB_BaconUps_043': {'triple_of': 'EX1_531'},

    # Spawn of N'Zoth
    'OG_256': {
        Event.DEATHRATTLE: lambda g, minion: g.buff(g.get_friendlies(minion), 1, 1)
    },
    'TB_BaconUps_025': {'triple_of': 'OG_256'},

    # Unstable Ghoul
    'FP1_024': {
        Event.DEATHRATTLE: lambda g, minion: g.damage(g.get_all_minions(), minion, damage=1)
    },
    'TB_BaconUps_118': {
        'triple_of': 'FP1_024',
        Event.DEATHRATTLE: lambda g, minion: g.damage(g.get_all_minions(), minion, damage=2)
    },


    #
    # Tier 3
    #

    # # Hangry Dragon
    # 'BGS_033': {
    #     Start of Turn: Gain +2/+2 if you won the last Combat
    # },
    # 'TB_BaconUps_104': {'triple_Of': 'BGS_033'},

    # The Beast
    'EX1_577': {
        Event.DEATHRATTLE: lambda g, minion: g.summon(g.get_enemies(minion, allow_dead=True)[-1], 'EX1_finkle')
    },
    'TB_BaconUps_042': {
        'triple_of': 'EX1_577',
        Event.DEATHRATTLE: lambda g, minion: g.summon(g.get_enemies(minion, allow_dead=True)[-1], 'EX1_finkle')
    },

    # Piloted Shredder
    'BGS_023': {
        Event.DEATHRATTLE: lambda g, minion: g.summon(minion, get_random_card_id('BGS_023', TECH_LEVEL=2))
    },
    'TB_BaconUps_035': {'triple_of': 'BGS_023'},

    # Cobalt Guardian
    'GVG_062': {
        Event.FRIENDLY_MINION_SUMMONED: lambda g, minion, target: \
            g.buff([minion], divine_shield=True) if target.race == hearthstone.enums.Race.MECHANICAL else 0
    },

    # Imp Gang Boss
    'BRM_006': {
        Event.DAMAGE_RECEIVED: lambda g, minion, index: g.summon(minion, 'BRM_006t', index + 1)
    },
    'TB_BaconUps_030': {
        'triple_of': 'BRM_006',
        Event.DAMAGE_RECEIVED: lambda g, minion, index: g.summon(minion, 'TB_BaconUps_030t', index + 1)
    },

    # Infested Wolf
    'OG_216': {
        Event.DEATHRATTLE: lambda g, minion: [g.summon(minion, 'OG_216a') for i in range(2)]
    },
    'TB_BaconUps_026': {
        'triple_of': 'OG_216',
        Event.DEATHRATTLE: lambda g, minion: [g.summon(minion, 'TB_BaconUps_026t') for i in range(2)]
    },

    # Pack Leader
    'BGS_017': {
        Event.FRIENDLY_MINION_SUMMONED: lambda g, minion, target: \
            g.buff([target], 3, 0) if target.race == hearthstone.enums.Race.BEAST else 0
    },
    'TB_BaconUps_086': {'triple_of': 'BGS_017'},

    # Replicating Menace
    'BOT_312': {
        Event.DEATHRATTLE: lambda g, minion: g.summon(minion, 'BOT_312t', count=3)
    },
    'TB_BaconUps_032': {
        'triple_of': 'BOT_312',
        Event.DEATHRATTLE: lambda g, minion: g.summon(minion, 'TB_BaconUps_032t', count=3)
    },
    'BOT_312e': {
        'enchantment_of': 'BOT_312'
    },

    # Soul Juggler
    'BGS_002': {
        Event.MINION_DIED: lambda g, minion, target: \
            g.damage([g.get_random_enemy(minion)], minion, damage=3) \
                if (
                    target.race == hearthstone.enums.Race.DEMON and
                    target.controller_index == minion.controller_index
                ) else 0
    },
    'TB_BaconUps_075': {'triple_of': 'BGS_002'},


    #
    # Tier 4
    #

    # # Siegebreaker
    # 'EX1_185': {
    #     Your other demons have +1 Attack
    # },
    # 'TB_BaconUps_053': {'triple_of': 'EX1_185'},

    # Bolvar, Fireblood
    'ICC_858': {
        Event.FRIENDLY_MINION_LOST_DIVINE_SHIELD: lambda g, minion, target: g.buff([minion], 2, 0)
    },
    'TB_BaconUps_047': {'triple_of': 'ICC_858'},

    # Cave Hydra
    'LOOT_078': {
        'cleave': True
    },

    # Drakonid Enforcer
    'BGS_067': {
        Event.FRIENDLY_MINION_LOST_DIVINE_SHIELD: lambda g, minion, target: g.buff([minion], 2, 2)
    },
    'TB_BaconUps_117': {'triple_of': 'BGS_067'},

    # Herald of Flame
    'BGS_032': {
        Event.OVERKILL: lambda g, minion: g.damage([g.get_enemies(minion)[0]], minion, damage=3)
    },
    'TB_BaconUps_103': {
        'triple_of': 'BGS_032',
        Event.OVERKILL: lambda g, minion: g.damage([g.get_enemies(minion)[0]], minion, damage=6)
    },

    # Mechano-Egg
    'BOT_537': {
        Event.DEATHRATTLE: lambda g, minion: g.summon(minion, 'BOT_537t')
    },
    'TB_BaconUps_039': {
        'triple_of': 'BOT_537',
        Event.DEATHRATTLE: lambda g, minion: g.summon(minion, 'TB_BaconUps_039t')
    },

    # Security Rover
    'BOT_218': {
        Event.DAMAGE_RECEIVED: lambda g, minion, index: g.summon(minion, 'BOT_218t', index + 1)
    },
    'TB_BaconUps_041': {
        'triple_of': 'BOT_218',
        Event.DAMAGE_RECEIVED: lambda g, minion, index: g.summon(minion, 'TB_BaconUps_041t', index + 1)
    },


    #
    # Tier 5
    #

    # # Mal'Ganis
    # 'GVG_021': {
    #     Your other demons have +2/+2
    # },
    # 'TB_BaconUps_060': {'triple_of': 'GVG_021'},

    # Goldrinn, the Great Wolf
    'BGS_018': {
        Event.DEATHRATTLE: lambda g, minion: g.buff(g.get_friendlies(minion, race=hearthstone.enums.Race.BEAST), 4, 4)
    },
    'TB_BaconUps_085': {'triple_of': 'BGS_018'},

    # Ironhide Direhorn
    'TRL_232': {
        Event.OVERKILL: lambda g, minion: g.summon(minion, 'TRL_232t')
    },
    'TB_BaconUps_051': {
        'triple_of': 'TRL_232',
        Event.OVERKILL: lambda g, minion: g.summon(minion, 'TB_BaconUps_051t')
    },

    # Junkbot
    'GVG_106': {
        Event.MINION_DIED: lambda g, minion, target: \
            g.buff([minion], 2, 2) if (
                target.race == hearthstone.enums.Race.MECHANICAL and
                target.controller_index == minion.controller_index
            ) else 0
    },
    'TB_BaconUps_046': {'triple_of': 'GVG_106'},

    # King Bagurgle
    'BGS_030': {
        Event.DEATHRATTLE: lambda g, minion: g.buff(g.get_friendlies(minion, race=hearthstone.enums.Race.MURLOC), 2, 2)
    },
    'TB_BaconUps_100': {'triple_of': 'BGS_030'},

    # Savannah Highmane
    'EX1_534': {
        Event.DEATHRATTLE: lambda g, minion: [g.summon(minion, 'EX1_534t') for _ in range(2)]
    },
    'TB_BaconUps_049': {
        'triple_of': 'EX1_534',
        Event.DEATHRATTLE: lambda g, minion: [g.summon(minion, 'TB_BaconUps_049t') for _ in range(2)]
    },

    # Sneed's Old Shredder
    'BGS_006': {
        Event.DEATHRATTLE: lambda g, minion: g.summon(minion, get_random_card_id('BGS_006', RARITY=5))
    },
    'TB_BaconUps_080': {'triple_of': 'BGS_006'},

    # Voidlord
    'LOOT_368': {
        Event.DEATHRATTLE: lambda g, minion: [g.summon(minion, 'CS2_065') for _ in range(3)]
    },
    'TB_BaconUps_059': {
        'triple_of': 'LOOT_368',
        Event.DEATHRATTLE: lambda g, minion: [g.summon(minion, 'TB_BaconUps_059t') for _ in range(3)]
    },

    # Baron Rivendare (placeholder)
    'FP1_031': {Event.DEATHRATTLE: lambda g, minion: 0},
    'TB_BaconUps_055': {'triple_Of': 'FP1_031'},


    #
    # Tier 6
    #

    # Foe Reaper 4000
    'GVG_113': {'cleave': True},

    # Ghastcoiler
    'BGS_008': {
        Event.DEATHRATTLE: lambda g, minion: [g.summon(minion, get_random_card_id('BGS_008', DEATHRATTLE=1)) for _ in range(2)]
    },
    'TB_BaconUps_057': {'triple_of': 'BGS_008'},

    # Holy Mackerel
    'BGS_068': {
        Event.FRIENDLY_MINION_LOST_DIVINE_SHIELD: lambda g, minion, target: g.buff([minion], divine_shield=True)
    },

    # Imp Mama
    'BGS_044': {
        Event.DAMAGE_RECEIVED: lambda g, minion, index: \
            g.buff([
                g.summon(minion, get_random_card_id('BGS_044', CARDRACE='DEMON'), index + 1)
            ], taunt=True)
    },
    'TB_BaconUps_116': {'triple_of': 'BGS_044'},

    # Kangor's Apprentice
    'BGS_012': {
        Event.DEATHRATTLE: lambda g, minion: [
            g.summon(minion, mech.card_id) for mech in g.get_first_two_friendly_mechs_that_died(minion)
        ]
    },
    'TB_BaconUps_087': {'triple_of': 'BGS_012'},

    # Mama Bear
    'BGS_021': {
        Event.FRIENDLY_MINION_SUMMONED: lambda g, minion, target: \
            g.buff([target], 5, 5) if target.race == hearthstone.enums.Race.BEAST else 0
    },
    'TB_BaconUps_090': {'triple_of': 'BGS_021'},

    # Nadina the Red
    'BGS_040': {
        Event.DEATHRATTLE: lambda g, minion: g.buff(g.get_friendlies(minion, race=hearthstone.enums.Race.DRAGON), divine_shield=True)
    },


    #
    # Buffs
    #

    # Living Spores (from Gentle Megasaur)
    'UNG_999t2e': {
        Event.DEATHRATTLE: lambda g, minion: [g.summon(minion, 'UNG_999t2t1') for i in range(2)]
    },


    #
    # Removed minions
    #

    # Piloted Sky Golem
    'BGS_024': {
        Event.DEATHRATTLE: lambda g, minion: g.summon(minion, get_random_card_id('BGS_024', TECH_LEVEL=4))
    },
    'TB_BaconUps_050': {'triple_of': 'BGS_024'},

    # Mounted Raptor
    'BGS_025': {
        Event.DEATHRATTLE: lambda g, minion: g.summon(minion, get_random_card_id('BGS_024', TECH_LEVEL=1))
    },
    'TB_BaconUps_019': {'triple_of': 'BGS_025'},

    # Tortollan Shellraiser
    'UNG_037': {
        Event.DEATHRATTLE: lambda g, minion: g.buff([g.get_random_friendly(minion)], 1, 1)
    },

}
