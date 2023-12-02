from dataclasses import dataclass, field
import re

from utility.main import check, every_line, show

@dataclass
class Round:
    blue: int
    red: int
    green: int

    def power(self):
        return self.blue * self.red * self.green

my_round = Round(red=1, green=3, blue=4)
check(my_round.power(), 12)

@dataclass
class Game:
    idx: int
    rounds: list[Round] = field(default_factory=list)

    def calculate_minimum_cubes(self):
        max_round = Round(0, 0, 0)
        for round in self.rounds:
            max_round = Round(
                blue=max(max_round.blue, round.blue),
                red=max(max_round.red, round.red),
                green=max(max_round.green, round.green)
            )
        return max_round

my_game = Game(1, [Round(1, 0, 2), Round(4, 1, 3), Round(1, 0, 1)])
check(my_game.calculate_minimum_cubes(), Round(red=1, green=3, blue=4))

@dataclass
class State:
    max_cubes: Round
    possible_games: list[Game] = field(default_factory=list)
    impossible_games: list[Game] = field(default_factory=list)
    sum_powers: int = 0

def sum_possible_game_ids(state):
    return sum(game.idx for game in state.possible_games)

my_state = State(Round(1, 2, 3), [Game(1), Game(2)])
check(sum_possible_game_ids(my_state), 3)

def is_round_possible(state, round):
    if round.blue > state.max_cubes.blue:
        return False
    elif round.red > state.max_cubes.red:
        return False
    elif round.green > state.max_cubes.green:
        return False
    return True

check(is_round_possible(my_state, Round(1, 2, 3)), True)
check(is_round_possible(my_state, Round(2, 2, 3)), False)
check(is_round_possible(my_state, Round(1, 3, 3)), False)
check(is_round_possible(my_state, Round(1, 2, 4)), False)

def evaluate_game(state, game):
    if all(is_round_possible(state, round) for round in game.rounds):
        state.possible_games.append(game)
    else:
        state.impossible_games.append(game)

my_state = State(Round(1, 2, 3))
evaluate_game(my_state, Game(1, [Round(1, 2, 3)]))
check(my_state.possible_games, [Game(1, [Round(1, 2, 3)])])
check(my_state.impossible_games, [])

my_state = State(Round(1, 2, 3))
evaluate_game(my_state, Game(1, [Round(1, 2, 3), Round(1, 3, 3)]))
check(my_state.possible_games, [])
check(my_state.impossible_games, [Game(1, [Round(1, 2, 3), Round(1, 3, 3)])])

def parse_line(state, line, _idx):
    game_matches = re.match(r"Game (\d+): (.*)", line)
    if game_matches is None:
        return None
    idx = int(game_matches.group(1))
    rounds = re.split(r"\s*;\s*", game_matches.group(2))
    round_objs = []
    for round_str in rounds:
        red, green, blue = 0, 0, 0
        count_str = re.split(r"\s*,\s*", round_str)
        for count in count_str:
            (count, color) = re.split(r" ", count)
            if color == "blue":
                blue = int(count)
            elif color == "red":
                red = int(count)
            elif color == "green":
                green = int(count)
        round_objs.append(Round(blue, red, green))
    game = Game(idx, round_objs)
    state.sum_powers += game.calculate_minimum_cubes().power()
    return state

def calculate(filename):
    state = State(Round(14, 12, 13))
    every_line(state, filename, [parse_line])
    print(state.sum_powers)

calculate("trial.txt")
calculate("input.txt")

