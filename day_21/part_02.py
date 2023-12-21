from dataclasses import dataclass, field
from typing import Self

from utility.main import adj, check, every_line, pret, show


@dataclass(frozen=True, order=True)
class Vec:
    x: int
    y: int

    def add(self, other):
        return Vec(self.x + other.x, self.y + other.y)

    def neighbours(self) -> set[Self]:
        return {
            Vec(self.x + 1, self.y),
            Vec(self.x - 1, self.y),
            Vec(self.x, self.y + 1),
            Vec(self.x, self.y - 1),
        }

@dataclass
class Grid:
    blocks: set[Vec] = field(default_factory=set)

    def free_neighbours(self, vec: Vec) -> set[Vec]:
        return vec.neighbours().difference(self.blocks)

my_grid = Grid({Vec(0, 1)})
check(my_grid.free_neighbours(Vec(0, 0)), {
        Vec(0, 0 - 1),
        Vec(0 + 1, 0),
        Vec(0 - 1, 0),
})

EVEN = 0
ODD = 1

@dataclass
class State:
    grid: Grid = field(default_factory=Grid)
    parities: dict[int, set[Vec]] = field(default_factory=dict)
    new_cells: set[Vec] = field(default_factory=set)
    start: Vec = Vec(0, 0)
    width: int = 0
    height: int = 0

    def calc_reachable_plots(self, n: int) -> int:
        for n in range(1, n + 1):
            parity = n % 2
            new_new_cells = set()
            for cell in self.new_cells:
                if self.off_screen(cell):
                    exit(1)
                neighbours = self.grid.free_neighbours(cell)
                new_new_cells.update(
                    n for n in neighbours
                    if n not in self.parities[parity]
                )
                self.parities[parity].update(neighbours)
            self.new_cells.clear()
            self.new_cells.update(new_new_cells)
            print(n, len(new_new_cells), len(self.parities[n % 2]))
        return len(self.parities[n % 2])

    def viz(self):
        grid = []
        for y in range(0, self.height):
            row = []
            for x in range(0, self.width):
                pos = Vec(x, y)
                if pos in self.grid.blocks:
                    row.append("#")
                elif pos in self.parities[EVEN]:
                    row.append("O")
                elif pos in self.new_cells:
                    row.append("x")
                else:
                    row.append(".")
            grid.append("".join(row))
        show("\n".join(grid), clear=True)

    def off_screen(self, pos):
        if pos.x >= self.width:
            return True
        elif pos.x < 0:
            return True
        elif pos.y >= self.height:
            return True
        elif pos.y < 0:
            return True
        return False

def parse_line(state: State, line: str, y: int) -> State:
    state.height = y + 1
    state.width = len(line)
    for x, char in enumerate(line):
        pos = Vec(x, y)
        if char == "#":
            state.grid.blocks.add(pos)
        elif char == "S":
            state.start = pos
    return state

def calculate(filename, n: int):
    state = State()
    every_line(state, filename, [parse_line])
    state.parities[ODD] = set()
    state.parities[EVEN] = set()
    state.new_cells = {state.start}
    state.viz()
    return state.calc_reachable_plots(n)

pret("Input:", calculate("input_2.txt", 100000))
