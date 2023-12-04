
from dataclasses import dataclass, field
import re

from utility.main import check, every_line, pret

@dataclass
class Game:
    idx: int
    winners: set[int] = field(default_factory=set)
    candidates: list[int] = field(default_factory=list)

    def calculate_score(self):
        score = 0
        for candidate in self.candidates:
            if candidate in self.winners:
                if score == 0:
                    score = 1
                else:
                    score *= 2
        return score

my_game = Game(1, {41, 48, 83, 86, 17}, [83, 86,  6, 31, 17,  9, 48, 53])
check(my_game.calculate_score(), 8)

@dataclass
class State:
    games: list[Game] = field(default_factory=list)

    def calculate_total_scores(self):
        return sum(game.calculate_score() for game in self.games)

def parse_line(state, line, _idx):
    matches = re.match(r"Card\s*(\d+):\s+([\d ]*)\s+\|\s+([\d ]*)", line)
    if matches is None:
        raise Exception(f"Bad line '{line}'")
    game_idx = int(matches.group(1))
    winners = {int(numstr) for numstr in re.split(r"\s+", matches.group(2))}
    candidates = [int(numstr) for numstr in re.split(r"\s+", matches.group(3))]
    state.games.append(Game(game_idx, winners, candidates))
    return state

my_game = Game(1, {41, 48, 83, 86, 17}, [83, 86,  6, 31, 17,  9, 48, 53])
my_state = State()
parse_line(my_state, "Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53", 1)
check(my_state.games, [my_game])

def calculate(filename):
    state = State()
    state = every_line(state, filename, [parse_line])
    return state.calculate_total_scores()

pret("Result", calculate("trial.txt"))
pret("Result", calculate("input.txt"))
