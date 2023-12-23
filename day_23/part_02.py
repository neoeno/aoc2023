from collections import defaultdict
from dataclasses import dataclass, field
from heapq import heappop, heappush
import math
from typing import Self

from utility.main import check, every, every_line, imagify, pret, show


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
        if self.kind == "#":
            return set()
        else:
            return self.pos.ortho()

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
    Vec(x=1, y=0), Vec(x=1, y=2), Vec(x=2, y=1), Vec(x=0, y=1)
})
check(my_cell.entries(), {
    Vec(x=1, y=0), Vec(x=1, y=2), Vec(x=2, y=1), Vec(x=0, y=1)
})
my_cell = Cell(Vec(1, 1), "<")
check(my_cell.exits(), {
    Vec(x=1, y=0), Vec(x=1, y=2), Vec(x=2, y=1), Vec(x=0, y=1)
})
check(my_cell.entries(), {
    Vec(x=1, y=0), Vec(x=1, y=2), Vec(x=2, y=1), Vec(x=0, y=1)
})
my_cell = Cell(Vec(1, 1), "^")
check(my_cell.exits(), {
    Vec(x=1, y=0), Vec(x=1, y=2), Vec(x=2, y=1), Vec(x=0, y=1)
})
check(my_cell.entries(), {
    Vec(x=1, y=0), Vec(x=1, y=2), Vec(x=2, y=1), Vec(x=0, y=1)
})
my_cell = Cell(Vec(1, 1), "v")
check(my_cell.exits(), {
    Vec(x=1, y=0), Vec(x=1, y=2), Vec(x=2, y=1), Vec(x=0, y=1)
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
    _is_inroad: dict[Cell, bool] = field(default_factory=dict)
    _neighbours: dict[Cursor, set[tuple[Cursor, int]]] = field(default_factory=dict)
    _pairs: dict[tuple[Vec, Vec], int] = field(default_factory=dict)

    def count_junctions(self):
        seen: set[Vec] = set()
        to_see: set[Cursor] = {Cursor(self.start, self.start.add(Vec(0, -1)), frozenset())}
        edges: dict[Vec, set[tuple[Vec, int]]] = {}
        while len(to_see) != 0:
            current = to_see.pop()
            seen.add(current.pos)
            for curs, cost in self.neighbours(current):
                if current.pos not in edges:
                    edges[current.pos] = set()
                if curs.pos not in edges:
                    edges[curs.pos] = set()
                edges[current.pos].add((curs.pos, cost))
                edges[curs.pos].add((current.pos, cost))
                if curs.pos not in seen:
                    to_see.add(Cursor(curs.pos, curs.prev, frozenset()))

        self.viz2(seen, [])
        print(len(edges))
        print(edges)
        exit(1)

    def count_steps_in_longest_path(self):
        seen: set[Vec] = set()
        to_check: list[Cursor] = []
        starting_cursor = Cursor(self.start, self.start.add(GOING_UP), frozenset())
        to_check.append(starting_cursor)
        came_from: dict[Cursor, Cursor] = {}
        g_score: dict[Cursor, float] = defaultdict(lambda: math.inf)
        g_score[starting_cursor] = 0
        ends: set[Cursor] = set()
        n = 0

        while len(to_check) != 0:
            current = to_check.pop()
            seen.add(current.pos)
            n += 1
            if n % 1000 == 0:
                self.viz(seen, came_from, current)
            if current.pos == self.end:
                ends.add(current)
                print(-1*min(g_score[end] for end in ends))
            neighbours = self.neighbours(current)

            for (neighbour, cost) in neighbours:
                self._pairs[current.pos, neighbour.pos] = cost
                tentative_g_score = g_score[current] - cost
                if tentative_g_score < g_score[neighbour]:
                    came_from[neighbour] = current
                    g_score[neighbour] = tentative_g_score
                    if neighbour not in to_check:
                        to_check.append(neighbour)

        return -1*min(g_score[end] for end in ends)

    def reconstruct_path(self, came_from: dict[Cursor, Cursor], current: Cursor) -> list[Vec]:
        total_path: list[Vec] = []
        while current in came_from:
            current = came_from[current]
            total_path.append(current.pos)
        return list(reversed(total_path))

    def is_inroad(self, cell: Cell) -> int:
        if cell in self._is_inroad:
            return self._is_inroad[cell]
        all_entries = cell.entries()
        inroads = [
            self.cells[vec] for vec in all_entries
            if not self.off_screen(vec)
               and cell.pos in self.cells[vec].exits()
        ]
        self._is_inroad[cell] = len(inroads) > 2
        return self._is_inroad[cell]

    def neighbours(self, cursor: Cursor, cost = 1) -> set[tuple[Cursor, int]]:
        if cursor in self._neighbours and cost == 1:
            return self._neighbours[cursor]
        cell = self.cells[cursor.pos]
        exits = cell.exits()
        good_exits = set()
        for ext in exits:
            if self.off_screen(ext):
                continue
            elif cell.pos not in self.cells[ext].entries():
                continue
            if ext in cursor.inroads_visited:
                continue
            if ext == cursor.prev:
                continue
            inroads_visited = cursor.inroads_visited
            if self.is_inroad(cell):
                inroads_visited = frozenset({cell.pos, *cursor.inroads_visited})
            good_exits.add(Cursor(ext, cursor.pos, inroads_visited))
        if len(good_exits) == 1 and list(good_exits)[0].pos != self.end:
            result = self.neighbours(list(good_exits)[0], cost + 1)
        elif cost > 1:
            result = {(ext, cost) for ext in {cursor}}
        else:
            result = set()
            for ext in good_exits:
                if ext.pos == self.end:
                    result.add((ext, cost))
                else:
                    result.update(self.neighbours(ext, cost + 1))
        if cost == 1:
            self._neighbours[cursor] = result
            return self._neighbours[cursor]
        return result

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

    def viz(self, seen = {}, came_from = None, pos = None):
        grid = []
        for fr, to in self._pairs.keys():
            cost = self._pairs[(fr, to)]
            show(f"\"{fr}\" -> \"{to}\" [label=\"{cost}\"]")
        if came_from != None and pos != None:
            best_path_here = self.reconstruct_path(came_from, pos)
        else:
            best_path_here = []
        for y in range(0, self.height):
            row = []
            for x in range(0, self.width):
                pos = Vec(x, y)
                if pos in best_path_here:
                    row.append('Y')
                elif pos in seen:
                    row.append('R')
                elif self.cells[pos].kind == "#":
                    row.append('#')
                else:
                    row.append('#')
            grid.append("".join(row))
        imagify("show.png", grid)

    def viz2(self, highlight, highlight2):
        grid = []
        for y in range(0, self.height):
            row = []
            for x in range(0, self.width):
                pos = Vec(x, y)
                if pos in highlight2:
                    row.append('M')
                elif pos in highlight:
                    row.append('R')
                elif self.cells[pos].kind == "#":
                    row.append('#')
                else:
                    row.append('G')
            grid.append("".join(row))
        imagify("show2.png", grid)

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

# check(my_state.is_inroad(my_state.cells[Vec(1, 0)]), False)
# check(my_state.is_inroad(my_state.cells[Vec(1, 1)]), True)
# check(my_state.is_inroad(my_state.cells[Vec(1, 2)]), False)
# check(my_state.is_inroad(my_state.cells[Vec(7, 4)]), True)
# my_cursor = Cursor(Vec(6, 4), Vec(5, 4), frozenset())
# check(my_state.neighbours(my_cursor), {
#     Cursor(Vec(7, 4), Vec(6, 4), frozenset())
# })
# my_cursor = Cursor(Vec(6, 4), Vec(5, 4), frozenset({Vec(7, 4)}))
# check(my_state.neighbours(my_cursor), set())
# check(my_state.count_steps_in_longest_path(), 13)

def calculate(filename):
    state = State()
    every_line(state, filename, [parse_line])
    state.count_junctions()
    # print(state.end) #139,140
    # count = state.count_steps_in_longest_path()
    # state.viz()
    # return count

# pret("Trial:", calculate("trial.txt"))
pret("Input:", calculate("input.txt"))
# 5570 - too low
# 5766 - too low
# 5978 - too low
# 6106 - wrong
# 6333 - wrong
# 12810 - wrong
