from collections import defaultdict
from dataclasses import dataclass, field
from heapq import heappop, heappush
import math
from typing import Self

from utility.main import check, every_line, pret, show


@dataclass(frozen=True, order=True)
class Vec:
    x: int
    y: int

    def add(self, other):
        return Vec(self.x + other.x, self.y + other.y)

GOING_RIGHT = Vec(1, 0)
GOING_LEFT = Vec(-1, 0)
GOING_UP = Vec(0, -1)
GOING_DOWN = Vec(0, 1)
VERTICALS = {GOING_UP, GOING_DOWN}
HORIZONTALS = {GOING_LEFT, GOING_RIGHT}

@dataclass
class Cell:
    pos: Vec
    heat_loss: int

    def hdist(self, to: Vec) -> int:
        return abs(to.x - self.pos.x) + abs(to.y - self.pos.y)

    def __repr__(self):
        return str(self.heat_loss)

my_cell = Cell(Vec(1, 1), 3)
check(my_cell.hdist(Vec(10, 9)), 17)

@dataclass(frozen=True, order=True)
class Cart:
    pos: Vec
    direction: Vec
    track: int

    def neighbours(self) -> set[Self]:
        neighbours = set()
        if self.track < 4:
            neighbours.add(Cart(self.pos.add(self.direction), self.direction, self.track + 1))
        elif self.track < 10:
            neighbours.add(Cart(self.pos.add(self.direction), self.direction, self.track + 1))
            if self.direction in VERTICALS:
                neighbours.add(Cart(self.pos.add(GOING_LEFT), GOING_LEFT, 1))
                neighbours.add(Cart(self.pos.add(GOING_RIGHT), GOING_RIGHT, 1))
            if self.direction in HORIZONTALS:
                neighbours.add(Cart(self.pos.add(GOING_UP), GOING_UP, 1))
                neighbours.add(Cart(self.pos.add(GOING_DOWN), GOING_DOWN, 1))
        elif self.track == 10:
            if self.direction in VERTICALS:
                neighbours.add(Cart(self.pos.add(GOING_LEFT), GOING_LEFT, 1))
                neighbours.add(Cart(self.pos.add(GOING_RIGHT), GOING_RIGHT, 1))
            if self.direction in HORIZONTALS:
                neighbours.add(Cart(self.pos.add(GOING_UP), GOING_UP, 1))
                neighbours.add(Cart(self.pos.add(GOING_DOWN), GOING_DOWN, 1))
        else:
            raise Exception("Can't be over ten!")
        return neighbours

    def hdist(self, to: Vec) -> int:
        return abs(to.x - self.pos.x) + abs(to.y - self.pos.y)

my_cart = Cart(Vec(5, 5), GOING_RIGHT, 1)
check(my_cart.neighbours(), {
    Cart(Vec(6, 5), GOING_RIGHT, 2),
})
my_cart = Cart(Vec(5, 5), GOING_LEFT, 1)
check(my_cart.neighbours(), {
    Cart(Vec(4, 5), GOING_LEFT, 2),
})
my_cart = Cart(Vec(5, 5), GOING_UP, 1)
check(my_cart.neighbours(), {
    Cart(Vec(5, 4), GOING_UP, 2),
})
my_cart = Cart(Vec(5, 5), GOING_DOWN, 1)
check(my_cart.neighbours(), {
    Cart(Vec(5, 6), GOING_DOWN, 2),
})
my_cart = Cart(Vec(5, 5), GOING_DOWN, 3)
check(my_cart.neighbours(), {
    Cart(Vec(5, 6), GOING_DOWN, 4),
})
my_cart = Cart(Vec(5, 5), GOING_DOWN, 4)
check(my_cart.neighbours(), {
    Cart(Vec(5, 6), GOING_DOWN, 5),
    Cart(Vec(4, 5), GOING_LEFT, 1),
    Cart(Vec(6, 5), GOING_RIGHT, 1)
})
my_cart = Cart(Vec(5, 5), GOING_DOWN, 9)
check(my_cart.neighbours(), {
    Cart(Vec(5, 6), GOING_DOWN, 10),
    Cart(Vec(4, 5), GOING_LEFT, 1),
    Cart(Vec(6, 5), GOING_RIGHT, 1)
})
my_cart = Cart(Vec(5, 5), GOING_DOWN, 10)
check(my_cart.neighbours(), {
    Cart(Vec(4, 5), GOING_LEFT, 1),
    Cart(Vec(6, 5), GOING_RIGHT, 1)
})

@dataclass
class State:
    cells: dict[Vec, Cell] = field(default_factory=dict)
    start: Cart = Cart(Vec(0, 0), GOING_RIGHT, 0)
    end: Vec = Vec(0, 0)
    width: int = 0
    height: int = 0
    best_path: list[Vec] = field(default_factory=list)

    def find_path(self):
        to_check: list[tuple[float, Cart]] = []
        heappush(to_check, (self.start.hdist(self.end), self.start))
        came_from: dict[Cart, Cart] = {}
        g_score: dict[Cart, float] = defaultdict(lambda: math.inf)
        g_score[self.start] = 0
        f_score: dict[Cart, float] = defaultdict(lambda: math.inf)
        f_score[self.start] = self.start.hdist(self.end)
        seen: set[Vec] = set()
        clock = 0

        while len(to_check) != 0:
            _, current = heappop(to_check)
            if current.pos == self.end and current.track >= 4:
                self.best_path = self.reconstruct_path(came_from, current)
                return self.best_path
            if clock % 100 == 0:
                self.viz(seen)
            clock += 1

            for neighbour in current.neighbours():
                if self.off_screen(neighbour.pos):
                    continue

                neighbour_cell = self.cells[neighbour.pos]
                tentative_g_score = g_score[current] + neighbour_cell.heat_loss
                if tentative_g_score < g_score[neighbour]:
                    came_from[neighbour] = current
                    g_score[neighbour] = tentative_g_score
                    seen.add(neighbour.pos)
                    f_score[neighbour] = tentative_g_score + neighbour.hdist(self.end)
                    if neighbour not in to_check:
                        heappush(to_check, (f_score[neighbour], neighbour))

        raise Exception("Couldn't find path :(")

    def reconstruct_path(self, came_from: dict[Cart, Cart], current: Cart) -> list[Vec]:
        total_path: list[Vec] = []
        while current in came_from:
            current = came_from[current]
            total_path.append(current.pos)
        return list(reversed(total_path))

    def heat_value(self, path: list[Vec]):
        return sum(self.cells[pos].heat_loss for pos in path[1:]) + self.cells[self.end].heat_loss

    def viz(self, mark: set[Vec]):
        if mark is None:
            mark = set()
        grid = []
        for y in range(0, self.height):
            row = []
            for x in range(0, self.width):
                pos = Vec(x, y)
                if pos in mark:
                    row.append("*")
                elif self.cells[pos] == self.start:
                    row.append("S")
                elif self.cells[pos] == self.end:
                    row.append("E")
                elif pos in self.best_path:
                    row.append("*")
                elif pos in self.cells:
                    row.append(str(self.cells[pos]))
                else:
                    row.append("!")
            grid.append("".join(row))
        show("\n".join(grid), clear=True)

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

def parse_line(state: State, line: str, y: int) -> State:
    state.height = y + 1
    state.width = len(line)
    for x, char in enumerate(line):
        pos = Vec(x, y)
        state.cells[pos] = Cell(pos, int(char))
    return state

def calculate(filename):
    state = State()
    state = every_line(state, filename, [parse_line])
    state.end = Vec(state.width - 1, state.height - 1)
    path = state.find_path()
    # state.viz()
    return state.heat_value(path)

# pret("Trial", calculate("trial.txt"))
pret("Input", calculate("input.txt"))
