
from dataclasses import dataclass, field
from itertools import product
import re
from time import sleep

from utility.main import check, every_line, hrange, pret, show


@dataclass(frozen=True)
class Coord:
    x: int
    y: int

    def adjacents(self):
        return {
            Coord(self.x - 1, self.y - 1),
            Coord(self.x, self.y - 1),
            Coord(self.x + 1, self.y - 1),
            Coord(self.x + 1, self.y),
            Coord(self.x + 1, self.y + 1),
            Coord(self.x, self.y + 1),
            Coord(self.x - 1, self.y + 1),
            Coord(self.x - 1, self.y),
        }

check(Coord(1, 1).adjacents(), {Coord(x=0, y=1), Coord(x=1, y=2), Coord(x=2, y=1), Coord(x=0, y=0), Coord(x=2, y=0), Coord(x=0, y=2), Coord(x=2, y=2), Coord(x=1, y=0)})

@dataclass(frozen=True)
class GridNumber:
    coord: Coord
    width: int
    number: int

    def get_cells_covering(self):
        return {
            Coord(x, self.coord.y)
            for x in
            hrange(self.coord.x, self.coord.x + self.width - 1, self.width)
        }

my_number = GridNumber(Coord(1, 1), 3, 123)
check(my_number.get_cells_covering(), {Coord(1, 1), Coord(2, 1), Coord(3, 1)})

@dataclass
class GridSymbol:
    coord: Coord
    symbol: str

@dataclass
class State:
    grid_numbers: list[GridNumber] = field(default_factory=list)
    grid_symbols: list[GridSymbol] = field(default_factory=list)
    valid_part_numbers: set[GridNumber] = field(default_factory=set)
    cells_to_grid_numbers: dict[Coord, GridNumber] = field(default_factory=dict)

    def viz(self):
        show("", True)
        grid = []
        for y in range(0, 10):
            row = []
            for x in range(0, 10):
                if Coord(x, y) in self.cells_to_grid_numbers:
                    row.append("1")
                elif Coord(x, y) in {s.coord for s in self.grid_symbols}:
                    row.append("*")
                else:
                    row.append(".")
            grid.append("".join(row))
        show(", ".join(str(g.number) for g in self.valid_part_numbers))
        show("\n".join(grid))

    def get_valid_part_numbers(self):
        for symbol in self.grid_symbols:
            for coord in symbol.coord.adjacents():
                if coord in self.cells_to_grid_numbers:
                    self.valid_part_numbers.add(self.cells_to_grid_numbers[coord])

    def calculate_gear_ratios(self) -> list[int]:
        gear_ratios = []
        asterisk_symbols = [symbol for symbol in self.grid_symbols if symbol.symbol == "*"]
        for symbol in asterisk_symbols:
            adjacent_numbers = set()
            for coord in symbol.coord.adjacents():
                if coord in self.cells_to_grid_numbers:
                    adjacent_numbers.add(self.cells_to_grid_numbers[coord])
            if len(adjacent_numbers) == 2:
                g = list(adjacent_numbers)
                gear_ratios.append(g[0].number * g[1].number)
        return gear_ratios

    def sum_part_numbers(self):
        return sum(
            grid_number.number for grid_number in self.valid_part_numbers
        )

def parse_line(state: State, line, y):
    number_matches = re.finditer(r"\d+", line)
    grid_numbers = list(GridNumber(
            Coord(match.start(), y), len(match.group(0)), int(match.group(0))
        )
        for match in number_matches
    )
    state.grid_numbers = state.grid_numbers + grid_numbers
    for grid_number in grid_numbers:
        for coord in grid_number.get_cells_covering():
            state.cells_to_grid_numbers[coord] = grid_number
    symbol_matches = re.finditer(r"[^.\d]", line)
    state.grid_symbols = state.grid_symbols + list(
        GridSymbol(Coord(match.start(), y), match.group(0))
        for match in symbol_matches
    )
    return state

my_state = State()
parse_line(my_state, ".....+.58.", 5)
check(my_state.grid_numbers, [GridNumber(Coord(7, 5), 2, 58)])
check(my_state.grid_symbols, [GridSymbol(Coord(5, 5), "+")])

def calculate(filename):
    state = State()
    state = every_line(state, filename, [parse_line])
    state.get_valid_part_numbers()
    return sum(state.calculate_gear_ratios())

pret("Result:", calculate("trial.txt"))
pret("Result:", calculate("input.txt"))
