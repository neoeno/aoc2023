from dataclasses import dataclass, field
from math import floor

from utility.main import every_line, hrange, pret, show, tlog


@dataclass(frozen=True)
class Cell:
    x: int
    y: int

@dataclass
class Area:
    width: int = 0
    height: int = 0
    cells: set[Cell] = field(default_factory=set)
    rows: dict[int, set[int]] = field(default_factory=dict)
    cols: dict[int, set[int]] = field(default_factory=dict)

    def summarise(self):
        self.viz()
        check_col = 0
        for col in range(1, self.width):
            if self.col(col) == self.col(check_col):
                print("Match")
                print(check_col, col, self.width)
                if check_col == 0 or col == (self.width - 1):
                    print("Gotcha")
                    return floor((col + check_col) / 2) + 1
                check_col -= 1
            else:
                print("No match")
                check_col = col
        check_row = 0
        for row in range(1, self.height):
            if self.row(row) == self.row(check_row):
                print("Match")
                print(check_row, row, self.height)
                if check_row == 0 or row == (self.height - 1):
                    print("Gotcha")
                    return (floor((row + check_row) / 2) + 1)*100
                check_row -= 1
            else:
                print("No match")
                check_row = row
        raise Exception("No mirror found!")

    def row(self, n):
        if n in self.rows:
            return self.rows[n]
        row = {cell.x for cell in self.cells if cell.y == n}
        self.rows[n] = row
        return row

    def col(self, n):
        if n in self.cols:
            return self.cols[n]
        col = {cell.y for cell in self.cells if cell.x == n}
        self.cols[n] = col
        return col

    def viz(self):
        grid = []
        for y in range(0, self.height):
            row = []
            for x in range(0, self.width):
                if Cell(x, y) in self.cells:
                    row.append("#")
                else:
                    row.append(".")
            grid.append("".join(row))
        show("\n".join(grid), clear=True)

@dataclass
class State:
    areas: list[Area] = field(default_factory=list)
    current_area: Area | None = None
    area_started: int = 0

    def summarize(self):
        return sum(
            area.summarise() for area in self.areas)


def parse_line(state: State, line: str, lidx: int):
    if len(line.strip()) == 0 or state.current_area is None:
        if state.current_area is not None:
            state.areas.append(state.current_area)
        state.current_area = Area()
        state.area_started = lidx
    if len(line.strip()) == 0:
        state.area_started += 1
        return state
    y = lidx - state.area_started
    state.current_area.width = len(line)
    state.current_area.height = y + 1
    for x, c in enumerate(line):
        if c == "#":
            cell = Cell(x, y)
            state.current_area.cells.add(cell)
    return state

def calculate(filename):
    state = State()
    every_line(state, filename, [parse_line])
    if state.current_area is not None:
        state.areas.append(state.current_area)
        state.current_area = None
        state.area_started = 0
    # return [(area.width, area.height) for area in state.areas]
    return state.summarize()

pret("Trial:", calculate("trial.txt"))
pret("Input:", calculate("input.txt"))
