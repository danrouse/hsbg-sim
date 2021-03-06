import random
from typing import Optional, List, Any

from card_defs import card_defs
from card_effects import card_effects


class Entity():
    def __init__(
        self,
        card_id: str,
        id: Optional[Any] = None,

        attack: Optional[int] = None,
        health: Optional[int] = None,

        divine_shield: Optional[bool] = None,
        windfury: Optional[bool] = None,
        taunt: Optional[bool] = None,
        poisonous: Optional[bool] = None,
        reborn: Optional[bool] = None,
        deathrattle: Optional[bool] = None,

        tier: Optional[int] = None,

        enchantments: Optional[List[str]] = None,
        controller_index: Optional[int] = None
    ):
        self.id = id if id is not None else random.getrandbits(16) # NB: not particularly safe
        self.card_id = card_id

        card_def = card_defs.get(card_id)
        self.card_def = card_def
        self.effects = card_effects.get(card_id, {})

        self.attack = attack if attack is not None else card_def.get('ATK', 0)
        self.health = health if health is not None else card_def.get('HEALTH', 0)
        self.divine_shield = divine_shield if divine_shield is not None else card_def.get('DIVINE_SHIELD', False)
        self.windfury = windfury if windfury is not None else card_def.get('WINDFURY', False)
        self.taunt = taunt if taunt is not None else card_def.get('TAUNT', False)
        self.poisonous = poisonous if poisonous is not None else card_def.get('POISONOUS', False)
        self.reborn = reborn if reborn is not None else card_def.get('REBORN', False)
        self.deathrattle = deathrattle if deathrattle is not None else card_def.get('DEATHRATTLE', False)
        self.tier = tier if tier is not None else card_def.get('TECH_LEVEL', 0)

        self.enchantments = enchantments if enchantments is not None else []

        self.exhausted = False
        self.controller_index = controller_index

    @property
    def name(self):
        return self.card_def.get('CARDNAME', self.card_id)
    @property
    def race(self):
        return self.card_def.get('CARDRACE')
    @property
    def cleave(self):
        return self.effects.get('cleave', False)

    def __repr__(self):
        is_triple = bool('BaconUps' in self.card_id)
        buf = f"{self.attack}/{self.health} {self.name}{'+' if is_triple else ''} [{self.id}] "

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
