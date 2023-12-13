from dataclasses import dataclass, field
from math import ceil, floor
from tabnanny import check

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

    def summarize_new(self):
        found_col = self.mirror_col()
        found_row = self.mirror_row()
        found_second_col = self.mirror_col_new(found_col)
        found_second_row = self.mirror_row_new(found_row)

        if found_second_col == -1:
            assert found_second_row > 0
            return found_second_row * 100
        else:
            assert found_second_col > 0
            return found_second_col

    def summarize(self):
        if self.mirror_col() == -1:
            return (self.mirror_row() + 1) * 100
        else:
            return self.mirror_col() + 1

    def mirror_col(self):
        check_col = 0
        for col in range(1, self.width):
            if self.col(col) == self.col(check_col):
                if check_col == 0 or col == (self.width - 1):
                    return floor((col + check_col) / 2)
                check_col -= 1
            else:
                check_col = col
        return -1

    def mirror_col_new(self, without: int):
        without += 1
        check_col = 0
        smudges = 0
        col = 1
        while col < self.width:
            if (check_col == col - 1) and col == without:
                assert smudges == 0
                check_col = col
            elif self.col(col) == self.col(check_col):
                if check_col == 0 or col == (self.width - 1):
                    assert smudges == 1
                    return floor((col + check_col) / 2) + 1
                check_col -= 1
            elif smudges == 0 and self.one_off(self.col(col), self.col(check_col)):
                if check_col == 0 or col == (self.width - 1):
                    return floor((col + check_col) / 2) + 1
                smudges += 1
                check_col -= 1
            else:
                smudges = 0
                col = ceil((col + check_col) / 2)
                check_col = col
            col += 1

        return -1

    def mirror_row_new(self, without: int):
        without += 1
        check_row = 0
        smudges = 0
        row = 1
        while row < self.height:
            if (check_row == row - 1) and row == without:
                assert smudges == 0
                check_row = row
            elif self.row(row) == self.row(check_row):
                if check_row == 0 or row == (self.height - 1):
                    assert smudges == 1
                    return floor((row + check_row) / 2) + 1
                check_row -= 1
            elif smudges == 0 and self.one_off(self.row(row), self.row(check_row)):
                if check_row == 0 or row == (self.height - 1):
                    return floor((row + check_row) / 2) + 1
                smudges += 1
                check_row -= 1
            else:
                smudges = 0
                row = ceil((row + check_row) / 2)
                check_row = row
            row += 1
        return -1

    def one_off(self, a: set[int], b: set[int]):
        return len(a.symmetric_difference(b)) == 1

    def mirror_row(self):
        check_row = 0
        for row in range(1, self.height):
            if self.row(row) == self.row(check_row):
                if check_row == 0 or row == (self.height - 1):
                    return floor((row + check_row) / 2)
                check_row -= 1
            else:
                check_row = row
        return -1

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
        grid = ["   01234567890"]
        for y in range(0, self.height):
            row = [str(y).zfill(2), " "]
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
            area.summarize() for area in self.areas)

    def summarize_new(self):
        return sum(
            area.summarize_new() for area in self.areas)


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
    return state.summarize_new()

pret("Trial:", calculate("trial.txt"))
pret("Input:", calculate("input.txt"))
