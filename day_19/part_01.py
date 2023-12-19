from dataclasses import dataclass, field
from enum import Enum
import re
import sys
from typing import Self

from utility.main import check, every_line, pret

Trait = Enum("Trait", ["x", "m", "a", "s"])
INF = sys.maxsize
NINF = 0

@dataclass
class Item:
    traits: dict[Trait, int]

    def rating(self):
        return sum(self.traits.values())

@dataclass
class Ruleset:
    name: str
    rules: list[tuple[Trait, range, Self]] = field(default_factory=list)

    def dest(self, item: Item):
        return self.follow(item).name

    def follow(self, item: Item) -> Self:
        for trait, rule, dest in self.rules:
            if item.traits[trait] in rule:
                return dest
        raise Exception(f"Didn't match any rule in {self.name} for {item}")

my_ruleset = Ruleset("px", [
    (Trait.a, range(NINF, 2006), Ruleset("qkq")),
    (Trait.m, range(2091, INF), Ruleset("A")),
    (Trait.a, range(NINF, INF), Ruleset("rfg"))
])
my_item = Item({Trait.x: 0, Trait.m: 0, Trait.a: 2005, Trait.s: 0})
check(my_ruleset.dest(my_item), "qkq")
my_item = Item({Trait.x: 0, Trait.m: 0, Trait.a: 2006, Trait.s: 0})
check(my_ruleset.dest(my_item), "rfg")
my_item = Item({Trait.x: 0, Trait.m: 2090, Trait.a: 2006, Trait.s: 0})
check(my_ruleset.dest(my_item), "rfg")
my_item = Item({Trait.x: 0, Trait.m: 2091, Trait.a: 2006, Trait.s: 0})
check(my_ruleset.dest(my_item), "A")
my_item = Item({Trait.x: 0, Trait.m: 2092, Trait.a: 2006, Trait.s: 0})
check(my_ruleset.dest(my_item), "A")

@dataclass
class State:
    rulesets: dict[str, Ruleset] = field(default_factory=dict)
    items: list[Item] = field(default_factory=list)
    on_rulesets: bool = True

    def sum_accepted_ratings(self):
        return sum(item.rating() for item in self.items if self.is_accepted(item))

    def is_accepted(self, item: Item) -> bool:
        ruleset = self.rulesets["in"]
        visited = set()
        while ruleset.name not in visited:
            visited.add(ruleset.name)
            ruleset = ruleset.follow(item)
            if ruleset == self.rulesets["A"]:
                return True
            elif ruleset == self.rulesets["R"]:
                return False
        print("Cycle detected! Rejecting")
        return False


def parse_line(state: State, line: str, _idx: int) -> State:
    if line.strip() == "":
        state.on_rulesets = False
        return state
    if state.on_rulesets:
        matches = re.match(r"([a-zA-Z]+)\{(.*)\}", line)
        if matches is None:
            raise Exception(f"Can't parse line: {line}")
        if matches.group(1) in state.rulesets:
            ruleset = state.rulesets[matches.group(1)]
        else:
            state.rulesets[matches.group(1)] = ruleset = Ruleset(matches.group(1))
        rules = matches.group(2).split(",")
        for rule in rules[:-1]:
            if rule_matches := re.match(r"([xmas])([><])(\d+):([a-zA-Z]+)", rule):
                dest_name = rule_matches.group(4)
                if dest_name in state.rulesets:
                    dest_ruleset = state.rulesets[dest_name]
                else:
                    state.rulesets[dest_name] = dest_ruleset = Ruleset(dest_name)
                if rule_matches.group(2) == ">":
                    rule_tup = (Trait[rule_matches.group(1)], range(int(rule_matches.group(3)) + 1, INF), dest_ruleset)
                elif rule_matches.group(2) == "<":
                    rule_tup = (Trait[rule_matches.group(1)], range(NINF, int(rule_matches.group(3))), dest_ruleset)
                else:
                    raise Exception(f"Can't parse line: {line}")
                ruleset.rules.append(rule_tup)
            else:
                raise Exception(f"Can't parse line: {line}")
        if fallback_rule_matches := re.match(r"([a-zA-Z]+)", rules[-1]):
            fallback_rule_name = fallback_rule_matches.group(1)
            if fallback_rule_name in state.rulesets:
                fb_ruleset = state.rulesets[fallback_rule_name]
            else:
                state.rulesets[fallback_rule_name] = fb_ruleset = Ruleset(fallback_rule_name)
            ruleset.rules.append((Trait.x, range(NINF, INF), fb_ruleset))
        else:
            raise Exception(f"Can't parse line: {line}")
    else:
        if matches := re.match(r"{x=(\d+),m=(\d+),a=(\d+),s=(\d+)}", line):
            state.items.append(Item({
                Trait.x: int(matches.group(1)),
                Trait.m: int(matches.group(2)),
                Trait.a: int(matches.group(3)),
                Trait.s: int(matches.group(4)),
            }))
        else:
            raise Exception(f"Can't parse line: {line}")
    return state

def calculate(filename: str):
    state = State()
    every_line(state, filename, [parse_line])
    return state.sum_accepted_ratings()

pret("Trial", calculate("trial.txt"))
pret("Input", calculate("input.txt"))
