from dataclasses import dataclass
import re
from typing import Self

from utility.main import check, every_line, pret, show, tlog


@dataclass
class Cell:
    name: str
    left: Self | None = None
    right: Self | None = None

@dataclass
class Oscillator:
    dirs: str
    idx: int = 0

    def advance(self):
        self.idx = (self.idx + 1) % len(self.dirs)

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
class State:
    oscillator: Oscillator | None = None
    start: Cell | None = None
    end: Cell | None = None
    current: Cell | None = None
    cell_dict: dict[str, Cell] | None = None

    def advance(self):
        if self.current is None or self.oscillator is None:
            raise Exception("Class not set up")
        if self.oscillator.current() == "R":
            tlog(1, f"{self.current.name}:R -> {self.current.right.name}")
            self.current = self.current.right
        elif self.oscillator.current() == "L":
            tlog(1, f"{self.current.name}:L -> {self.current.right.name}")
            self.current = self.current.left
        else:
            raise Exception(f"Bad direction '{self.oscillator.current()}'")
        self.oscillator.advance()

    def steps_to_end(self):
        steps = 0
        while self.current is not self.end:
            self.advance()
            steps += 1
        return steps

a_cell = Cell("A")
b_cell = Cell("B")
z_cell = Cell("Z")
a_cell.left = b_cell
a_cell.right = b_cell
b_cell.left = a_cell
b_cell.right = z_cell
z_cell.left = z_cell
z_cell.right = z_cell
my_state = State(Oscillator("LLR"), a_cell, z_cell, a_cell)
my_state.advance()
check(my_state.current, b_cell)
my_state.advance()
check(my_state.current, a_cell)
my_state.advance()
check(my_state.current, b_cell)
my_state.advance()
check(my_state.current, a_cell)
my_state.advance()
check(my_state.current, b_cell)
my_state.advance()
check(my_state.current, z_cell)

my_state = State(Oscillator("LLR"), a_cell, z_cell, a_cell)
check(my_state.steps_to_end(), 6)

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
        state.cell_dict[matches.group(1)].left = state.cell_dict[matches.group(2)]
        state.cell_dict[matches.group(1)].right = state.cell_dict[matches.group(3)]
        return state
    else:
        return state


def compute(filename):
    cell_dict = {}
    cell_dict = every_line(cell_dict, filename, [parse_line_for_cell_dict])
    state = State()
    state.cell_dict = cell_dict
    state.start = state.current = state.cell_dict["AAA"]
    state.end = state.cell_dict["ZZZ"]
    state = every_line(state, filename, [parse_line])
    return state.steps_to_end()


pret("Trial result:", compute("trial.txt"))
pret("Trial 2 result:", compute("trial_2.txt"))
pret("Input result:", compute("input.txt"))
