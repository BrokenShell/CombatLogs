from Fortuna import dice, d


class Resource:

    def __init__(self, amount: int):
        self.maximum = amount
        self.current = amount

    def __sub__(self, amount: int):
        self.current -= amount
        return self

    def __add__(self, amount: int):
        self.current = min(self.current + amount, self.maximum)
        return self

    def __bool__(self):
        return self.current > 0

    def __str__(self):
        return f"{self.current}/{self.maximum}"


class CombatUnit:
    name: str
    hit_dice: int
    damage_dice: int
    offense: int
    defense: int

    def __init__(self, level):
        self.level = level
        self.health = Resource(dice(self.level, self.hit_dice) + self.hit_dice)
        self.n_specials = self.level // 5

    def __bool__(self):
        return bool(self.health)

    def damage(self):
        return dice(self.level, self.damage_dice)

    def attack(self, other):
        if self.n_specials > 0:
            self.n_specials -= 1
            self.special(other)
        else:
            if d(20) + self.offense > d(20) + other.defense:
                other.health -= self.damage()

    def special(self, other):
        if d(20) + self.offense > d(20) + other.defense:
            other.health -= self.damage() + self.damage_dice


class Barbarian(CombatUnit):
    name = "Barbarian"
    hit_dice = 10
    damage_dice = 6
    offense = 3
    defense = 2

    def special(self, other):
        """ Rampage - imposes disadvantage on the defender """
        disadvantage = min((d(20), d(20))) + other.defense
        if d(20) + self.offense > disadvantage:
            other.health -= self.damage()


class Bard(CombatUnit):
    name = "Bard"
    hit_dice = 6
    damage_dice = 6
    offense = 2
    defense = 3

    def special(self, other):
        """ Inspiration - increase damage delt """
        if d(20) + self.offense > d(20) + other.defense:
            other.health -= self.damage() + self.damage()


class Rogue(CombatUnit):
    name = "Rogue"
    hit_dice = 6
    damage_dice = 10
    offense = 4
    defense = 1

    def special(self, other):
        """ Backstab - triple damage if the rogue has not taken damage """
        if d(20) + self.offense > d(20) + other.defense:
            other.health -= self.damage() + self.damage()


# Todo: add these
"""
Mage
Paladin
Monk
Druid
"""
