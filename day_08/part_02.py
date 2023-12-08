from dataclasses import dataclass, field
from math import prod
import math
import re
from typing import Self

from utility.main import check, every_line, pret, show, tlog


@dataclass
class Cell:
    name: str
    left: Self | None = None
    right: Self | None = None

    def __repr__(self):
        return f"Cell({self.name})"

@dataclass
class Oscillator:
    dirs: str
    idx: int = 0

    def advance(self, n = 1):
        self.idx = (self.idx + n) % len(self.dirs)

    def current(self):
        return self.dirs[self.idx]

my_osc = Oscillator("LR", 0)
check(my_osc.current(), "L")
my_osc.advance()
check(my_osc.current(), "R")
my_osc.advance()
check(my_osc.current(), "L")
my_osc.advance()
check(my_osc.current(), "R")

@dataclass
class Head:
    current: Cell | None = None
    skip: int = 0
    after_skip: Cell | None = None
    last_z_cell: Cell | None = None
    last_z_steps: int | None = None

    def winning(self):
        if self.current is None:
            return False
        return self.current.name[-1] == "Z"

    def skipping(self):
        return self.skip != 0

    def recording(self):
        return self.last_z_cell is not None

@dataclass
class State:
    oscillator: Oscillator | None = None
    heads: list[Head] = field(default_factory=list)
    skips: dict[tuple[str, int], tuple[int, Cell]] = field(default_factory=dict)
    cell_dict: dict[str, Cell] | None = None

    def steps_to_end(self):
        if self.oscillator is None:
            raise Exception("Class not set up")
        steps = 0
        while True:
            for head in self.heads:
                if head.winning() and head.current is not None:
                    if (head.current.name, self.oscillator.idx) in self.skips:
                        skip_data = self.skips[(head.current.name, self.oscillator.idx)]
                        head.skip = skip_data[0]
                    elif head.recording() and head.last_z_steps is not None and head.last_z_cell is not None:
                        skip_length = steps - head.last_z_steps
                        tlog(1, f"New skip found at {steps}: {head.last_z_cell.name}:{self.oscillator.idx} -{skip_length}-> {head.current.name}")
                        self.skips[(head.last_z_cell.name, self.oscillator.idx)] = (skip_length, head.current)
                        head.last_z_cell = head.current
                        head.last_z_steps = steps
                    else:
                        head.last_z_cell = head.current
                        head.last_z_steps = steps
            if self.all_skipping():
                return math.lcm(*list(skip[0] for skip in self.skips.values()))
            else:
                for head in self.heads:
                    if self.oscillator.current() == "R":
                        head.current = head.current.right
                    elif self.oscillator.current() == "L":
                        head.current = head.current.left
                    else:
                        raise Exception(f"Bad direction '{self.oscillator.current()}'")
                self.oscillator.advance()
                steps += 1

    def all_winning(self):
        return all(head.winning() for head in self.heads)

    def all_skipping(self):
        return all(head.skipping() for head in self.heads)

def parse_line_for_cell_dict(state, line, idx):
    if idx <= 1:
        return state
    state[line[0:3]] = Cell(line[0:3])
    return state

def parse_line(state, line, idx):
    if idx == 0:
        state.oscillator = Oscillator(line)
        return state
    elif idx > 1:
        matches = re.match(r"([A-Z]+) = \(([A-Z]+), ([A-Z]+)\)", line)
        if matches is None:
            raise Exception(f"Bad line: {line}")
        this_cell = state.cell_dict[matches.group(1)]
        this_cell.left = state.cell_dict[matches.group(2)]
        this_cell.right = state.cell_dict[matches.group(3)]
        if matches.group(1)[2] == "A":
            state.heads.append(Head(this_cell))
        return state
    else:
        return state


def compute(filename):
    cell_dict = {}
    cell_dict = every_line(cell_dict, filename, [parse_line_for_cell_dict])
    state = State()
    state.cell_dict = cell_dict
    state = every_line(state, filename, [parse_line])
    return state.steps_to_end()


# pret("Trial 2 result:", compute("trial_2.txt"))
pret("Input result:", compute("input.txt"))

# Not 35425771156910852049249195 -- too high
# Not 515051047497674924930031 -- too high
# Not 458146725334056242782752 -- too high
# Not 448870562260656801 -- unknown
#     20220305520997
#     37357320762
# 5m 15:03

# skips = [
#     (24166, 12083),
#     (34282, 17141),
#     (37654, 18827),
#     (39902, 19951),
#     (41026, 20513),
#     (44398, 22199)
# ]
# n = 20220305520997
# while True:
#     candidates = [s[0] + s[1] * n for s in skips]
#     if candidates.count(candidates[0]) == len(candidates):
#         pret("Result:", n)
#         print(candidates)
#         exit()
#     n += 1
#     if n % 1000000 == 0:
#         pret("n:", n)

# # y = 12083x + 24166 # 0
# # y = 17141x + 34282 # 0
# # y = 18827x + 37654 # 0
# # y = 19951x + 39902 # 0
# # y = 20513x + 41026 # 0
# # y = 22199x + 44398 # 0

# # 12083x + 24166 = 17141x + 34282

# # ax + b = cx + d
# # x = (d - b) / (a - c)

# # x = (34282 - 24166) / (12083 - 17141)
# # x = -2
