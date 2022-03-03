import csv

from Fortuna import dice, d, RandomValue


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
        """ Backstab - triple damage if the Rogue is at full health """
        triple_damage = self.damage() + self.damage() + self.damage()
        if d(20) + self.offense > d(20) + other.defense:
            if self.health.current == self.health.maximum:
                other.health -= triple_damage
            else:
                other.health -= self.damage()


class Wizard(CombatUnit):
    name = "Wizard"
    hit_dice = 4
    damage_dice = 12
    offense = 5
    defense = 0

    def special_attack(self, other):
        """ Magic Missile - always a hit """
        other.health -= self.damage()


class Warlock(CombatUnit):
    name = "Warlock"
    hit_dice = 8
    damage_dice = 8
    offense = 3
    defense = 2

    def special_attack(self, other):
        """ Demonic Empowerment - deals double damage """
        double_damage = self.damage() + self.damage()
        if d(20) + self.offense > d(20) + other.defense:
            other.health -= double_damage


class Necromancer(CombatUnit):
    name = "Necromancer"
    hit_dice = 6
    damage_dice = 10
    offense = 3
    defense = 2

    def special_attack(self, other):
        """ Siphon Soul - heal for the amount of damage dealt """
        damage = self.damage()
        if d(20) + self.offense > d(20) + other.defense:
            other.health -= damage
            self.health += damage


class Archer(CombatUnit):
    name = "Archer"
    hit_dice = 6
    damage_dice = 10
    offense = 4
    defense = 1

    def special_attack(self, other):
        """ Steady Aim - grants advantage to the attacker """
        advantage = max(d(20), d(20)) + self.offense
        if advantage > d(20) + other.defense:
            other.health -= self.damage()


class Ninja(CombatUnit):
    name = "Ninja"
    hit_dice = 4
    damage_dice = 12
    offense = 4
    defense = 1

    def special_attack(self, other):
        """ Ambush - grants a bonus attack to the attacker,
            first attack has advantage,
            second attack has disadvantage """
        first_attack = max(d(20), d(20)) + self.offense
        if first_attack > d(20) + other.defense:
            other.health -= self.damage()
        second_attack = min(d(20), d(20)) + self.offense
        if second_attack > d(20) + other.defense:
            other.health -= self.damage()


class Paladin(CombatUnit):
    name = "Paladin"
    hit_dice = 10
    damage_dice = 6
    offense = 2
    defense = 3

    def special(self, other):
        """ Hammer of Light - heals the Paladin, then if the attack is a hit,
         deals the same amount of damage to the defender """
        damage = self.damage()
        self.health += damage
        if d(20) + self.offense > d(20) + other.defense:
            other.health -= damage


class Druid(CombatUnit):
    name = "Druid"
    hit_dice = 8
    damage_dice = 8
    offense = 1
    defense = 4


class Monk(CombatUnit):
    name = "Monk"
    hit_dice = 6
    damage_dice = 10
    offense = 1
    defense = 4


class Pirate(CombatUnit):
    name = "Pirate"
    hit_dice = 8
    damage_dice = 8
    offense = 3
    defense = 2


def combat(attacker: CombatUnit, defender: CombatUnit):
    while attacker and defender:
        attacker.attack(defender)
        defender.attack(attacker)
    if attacker:
        return attacker.name
    elif defender:
        return defender.name
    else:
        return "Draw"


def campaign():
    random_class = RandomValue((
        Barbarian,
        Bard,
        Rogue,
        Wizard,
        Warlock,
        Necromancer,
        Archer,
        Ninja,
        Paladin,
        Druid,
        Monk,
        Pirate,
    ))

    with open('combat_log.csv', 'w') as csv_file:
        file = csv.writer(csv_file, delimiter=',')
        file.writerow((
            "Attacker", "AttackerLevel",
            "Defender", "DefenderLevel",
            "Winner"
        ))
        for _ in range(100000):
            attacker = random_class(dice(1, 20))
            defender = random_class(dice(1, 20))
            file.writerow((
                attacker.name, attacker.level,
                defender.name, defender.level,
                combat(attacker, defender)
            ))


if __name__ == '__main__':
    campaign()
