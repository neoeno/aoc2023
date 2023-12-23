from collections import defaultdict
from dataclasses import dataclass, field
from heapq import heappop, heappush
import math
from typing import Self

from utility.main import check, every, every_line, pret, show


@dataclass(frozen=True, order=True)
class Vec:
    x: int
    y: int

    def add(self, other):
        return Vec(self.x + other.x, self.y + other.y)

    def hdist(self, to: Self) -> int:
        return abs(to.x - self.x) + abs(to.y - self.y)

    def ortho(self):
        return {
            Vec(self.x, self.y - 1),
            Vec(self.x + 1, self.y),
            Vec(self.x, self.y + 1),
            Vec(self.x - 1, self.y),
        }

GOING_RIGHT = Vec(1, 0)
GOING_LEFT = Vec(-1, 0)
GOING_UP = Vec(0, -1)
GOING_DOWN = Vec(0, 1)

@dataclass(frozen=True)
class Cell:
    pos: Vec
    kind: str

    def exits(self) -> set[Vec]:
        if self.kind == ".":
            return self.pos.ortho()
        elif self.kind == ">":
            return { self.pos.add(GOING_RIGHT) }
        elif self.kind == "<":
            return { self.pos.add(GOING_LEFT) }
        elif self.kind == "^":
            return { self.pos.add(GOING_UP) }
        elif self.kind == "v":
            return { self.pos.add(GOING_DOWN) }
        else:
            return set()

    def entries(self) -> set[Vec]:
        if self.kind == "#":
            return set()
        return self.pos.ortho()


my_cell = Cell(Vec(1, 1), ".")
my_cell = Cell(Vec(1, 1), ".")
check(my_cell.exits(), {
    Vec(x=1, y=0), Vec(x=1, y=2), Vec(x=2, y=1), Vec(x=0, y=1)
})
check(my_cell.entries(), {
    Vec(x=1, y=0), Vec(x=1, y=2), Vec(x=2, y=1), Vec(x=0, y=1)
})
my_cell = Cell(Vec(1, 1), ">")
check(my_cell.exits(), {
    Vec(x=2, y=1)
})
check(my_cell.entries(), {
    Vec(x=1, y=0), Vec(x=1, y=2), Vec(x=2, y=1), Vec(x=0, y=1)
})
my_cell = Cell(Vec(1, 1), "<")
check(my_cell.exits(), {
    Vec(x=0, y=1)
})
check(my_cell.entries(), {
    Vec(x=1, y=0), Vec(x=1, y=2), Vec(x=2, y=1), Vec(x=0, y=1)
})
my_cell = Cell(Vec(1, 1), "^")
check(my_cell.exits(), {
    Vec(x=1, y=0)
})
check(my_cell.entries(), {
    Vec(x=1, y=0), Vec(x=1, y=2), Vec(x=2, y=1), Vec(x=0, y=1)
})
my_cell = Cell(Vec(1, 1), "v")
check(my_cell.exits(), {
    Vec(x=1, y=2)
})
check(my_cell.entries(), {
    Vec(x=1, y=0), Vec(x=1, y=2), Vec(x=2, y=1), Vec(x=0, y=1)
})
my_cell = Cell(Vec(1, 1), "#")
check(my_cell.exits(), set())
check(my_cell.entries(), set())

@dataclass(frozen=True, order=True)
class Cursor:
    pos: Vec
    prev: Vec
    inroads_visited: frozenset[Vec]

@dataclass
class State:
    cells: dict[Vec, Cell] = field(default_factory=dict)
    start: Vec = Vec(1, 0)
    end: Vec = Vec(0, 0)
    height: int = 0
    width: int = 0
    focus: Vec = Vec(0, 0)
    best_path: list[Vec] = field(default_factory=list)

    def count_steps_in_longest_path(self):
        to_check: list[tuple[float, Cursor]] = []
        starting_cursor = Cursor(self.start, self.start.add(GOING_UP), frozenset())
        heappush(to_check, (self.start.hdist(self.end), starting_cursor))
        came_from: dict[Cursor, Cursor] = {}
        g_score: dict[Cursor, float] = defaultdict(lambda: math.inf)
        g_score[starting_cursor] = 0
        f_score: dict[Cursor, float] = defaultdict(lambda: math.inf)
        f_score[starting_cursor] = self.start.hdist(self.end)
        ends: set[Cursor] = set()

        while len(to_check) != 0:
            _, current = heappop(to_check)
            if current.pos == self.end:
                ends.add(current)

            for neighbour in self.neighbours(current):
                tentative_g_score = g_score[current] - 1
                if tentative_g_score < g_score[neighbour]:
                    came_from[neighbour] = current
                    g_score[neighbour] = tentative_g_score
                    f_score[neighbour] = tentative_g_score - neighbour.pos.hdist(self.end)
                    if neighbour not in to_check:
                        heappush(to_check, (f_score[neighbour], neighbour))

        return min(len(self.reconstruct_path(came_from, end)) for end in ends)

    def reconstruct_path(self, came_from: dict[Cursor, Cursor], current: Cursor) -> list[Vec]:
        total_path: list[Vec] = []
        while current in came_from:
            current = came_from[current]
            total_path.append(current.pos)
        return list(reversed(total_path))

    def is_inroad(self, cell: Cell) -> int:
        all_entries = cell.entries()
        inroads = [
            self.cells[vec] for vec in all_entries
            if not self.off_screen(vec)
               and cell.pos in self.cells[vec].exits()
        ]
        return len(inroads) > 2

    def neighbours(self, cursor: Cursor) -> set[Cursor]:
        cell = self.cells[cursor.pos]
        exits = cell.exits()
        good_exits = set()
        for ext in exits:
            if self.off_screen(ext):
                continue
            if cell.pos not in self.cells[ext].entries():
                continue
            if ext in cursor.inroads_visited:
                continue
            if ext == cursor.prev:
                continue
            inroads_visited = cursor.inroads_visited
            if self.is_inroad(cell):
                inroads_visited = frozenset({cell.pos, *cursor.inroads_visited})
            good_exits.add(Cursor(ext, cursor.pos, inroads_visited))
        return good_exits

    def off_screen(self, pos: Vec):
        if pos.x >= self.width:
            return True
        elif pos.x < 0:
            return True
        elif pos.y >= self.height:
            return True
        elif pos.y < 0:
            return True
        return False

    def viz(self):
        grid = []
        for y in range(0, self.height):
            row = []
            for x in range(0, self.width):
                pos = Vec(x, y)
                if pos == self.focus:
                    row.append('*')
                elif pos in self.best_path:
                    row.append('O')
                else:
                    row.append(self.cells[pos].kind)
            grid.append("".join(row))
        show("\n".join(grid), clear=True)

def parse_line(state: State, line: str, y: int) -> State:
    state.height = y + 1
    state.width = len(line)
    state.end = Vec(state.width - 2, state.height - 1)
    for x, char in enumerate(line):
        pos = Vec(x, y)
        state.cells[pos] = Cell(pos, char)
    return state

my_state = every(State(), [
    "#.###",
    "#...#",
    "###.#",
], [parse_line])
my_state.viz()

my_state = every(State(), [
    "#.#######",
    "#.>.#...#",
    "#v#...#.#",
    "#.#####v#",
    "#.......#",
    "#######.#",
], [parse_line])

check(my_state.is_inroad(my_state.cells[Vec(1, 0)]), False)
check(my_state.is_inroad(my_state.cells[Vec(1, 1)]), False)
check(my_state.is_inroad(my_state.cells[Vec(1, 2)]), False)
check(my_state.is_inroad(my_state.cells[Vec(7, 4)]), True)
my_cursor = Cursor(Vec(6, 4), Vec(5, 4), frozenset())
check(my_state.neighbours(my_cursor), {
    Cursor(Vec(7, 4), Vec(6, 4), frozenset())
})
my_cursor = Cursor(Vec(6, 4), Vec(5, 4), frozenset({Vec(7, 4)}))
check(my_state.neighbours(my_cursor), set())
check(my_state.count_steps_in_longest_path(), 13)

def calculate(filename):
    state = State()
    every_line(state, filename, [parse_line])
    count = state.count_steps_in_longest_path()
    state.focus = Vec(13, 13)
    state.viz()
    return count

pret("Trial:", calculate("trial.txt"))
pret("Input:", calculate("input.txt"))
