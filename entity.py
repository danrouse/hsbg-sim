from uuid import uuid4

from card_defs import card_defs
from card_effects import card_effects


class Entity():
    def __init__(
        self,
        card_id,
        id=None,

        attack=None,
        health=None,

        divine_shield=None,
        windfury=None,
        taunt=None,
        poisonous=None,
        reborn=None,
        deathrattle=None,

        enchantments=None,
        controller_index=None
    ):
        self.id = id if id is not None else uuid4()
        self.card_id = card_id

        self.card_def = card_defs.get(card_id, {})
        self.effects = card_effects.get(card_id, {})

        self.attack = attack if attack is not None else self.card_def.get('ATK', 0)
        self.health = health if health is not None else self.card_def.get('HEALTH', 0)
        self.divine_shield = divine_shield if divine_shield is not None else bool(int(self.card_def.get('DIVINE_SHIELD', 0)))
        self.windfury = windfury if windfury is not None else bool(int(self.card_def.get('WINDFURY', 0)))
        self.taunt = taunt if taunt is not None else bool(int(self.card_def.get('TAUNT', 0)))
        self.poisonous = poisonous if poisonous is not None else bool(int(self.card_def.get('POISONOUS', 0)))
        self.reborn = reborn if reborn is not None else bool(int(self.card_def.get('REBORN', 0)))
        self.deathrattle = deathrattle if deathrattle is not None else bool(int(self.card_def.get('DEATHRATTLE', 0)))

        self.race = self.card_def.get('CARDRACE')
        self.tier = self.card_def.get('TECH_LEVEL', 0)
        self.name = self.card_def.get('CARDNAME')
        self.cleave = self.effects.get('cleave')

        self.enchantments = enchantments if enchantments is not None else []

        self.exhausted = False
        self.will_die = False
        self.controller_index = controller_index

    def __repr__(self):
        name = self.card_def.get('CARDNAME', self.card_id)
        is_triple = bool('BaconUps' in self.card_id)
        buf = f"{self.attack}/{self.health} {name}{'+' if is_triple else ''} [{self.id}] "
        # buf += "[{self.card_id}] "

        buffs = []
        if self.taunt: buffs.append('Taunt')
        if self.divine_shield: buffs.append('Divine Shield')
        if self.poisonous: buffs.append('Poisonous')
        if self.windfury: buffs.append('Windfury')
        if self.reborn: buffs.append('Reborn')
        # if self.deathrattle: buffs.append('Deathrattle')
        if buffs:
            buf += f" ({', '.join(buffs)})"

        return buf

    def __eq__(self, other):
        return self.id == other.id

    def clone(self):
        return Entity(
            card_id=self.card_id,
            id=self.id,
            attack=self.attack,
            health=self.health,
            divine_shield=self.divine_shield,
            windfury=self.windfury,
            taunt=self.taunt,
            poisonous=self.poisonous,
            reborn=self.reborn,
            deathrattle=self.deathrattle,
            enchantments=self.enchantments,
            controller_index=self.controller_index
        )
