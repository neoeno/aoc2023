from dataclasses import dataclass, field

from utility.main import every_line, pret, show

@dataclass(frozen=True)
class Vec:
    x: int
    y: int

    def add(self, vec):
        return Vec(self.x + vec.x, self.y + vec.y)

@dataclass
class Cell:
    pos: Vec
    type: str

@dataclass
class Grid:
    location_to_cell: dict[Vec, Cell] = field(default_factory=dict)

    def get_type(self, pos: Vec) -> str:
        if pos not in self.location_to_cell:
            return "."
        return self.location_to_cell[pos].type

    def add(self, cell: Cell):
        self.location_to_cell[cell.pos] = cell

@dataclass
class Searcher:
    pos: Vec = Vec(0, 0)
    last_movement: Vec = Vec(0, 0)
    steps: int = 0

    def move(self, by: Vec):
        if abs(by.x) + abs(by.y) != 1:
            raise Exception(f"Must move by 1 step, moved by {by}")
        self.steps += 1
        self.pos = self.pos.add(by)
        self.last_movement = by

@dataclass
class State:
    grid: Grid = field(default_factory=Grid)
    searcher_a: Searcher = field(default_factory=Searcher)
    searcher_b: Searcher = field(default_factory=Searcher)
    lookup: dict[tuple[Vec, str], Vec] = field(default_factory=dict)
    start_cell: Cell | None = None

    def tick(self, searcher: Searcher):
        searcher.move(State.lookup[searcher.last_movement, self.grid.get_type(searcher.pos)])

    def find_midpoint(self):
        self.setup_searchers()
        while self.searcher_a.pos != self.searcher_b.pos:
            self.tick(self.searcher_a)
            self.tick(self.searcher_b)
        if self.searcher_a.steps != self.searcher_b.steps:
            raise Exception(f"Steps different!")
        return self.searcher_a.steps

    def setup_searchers(self):
        directions = []
        if self.start_cell is None:
            raise Exception("No start cell!")
        pos = self.start_cell.pos
        if self.grid.get_type(pos.add(Vec(0, -1))) in ["|", "F", "7"]:
            directions.append(Vec(0, -1))
        if self.grid.get_type(pos.add(Vec(0, 1))) in ["|", "J", "L"]:
            directions.append(Vec(0, 1))
        if self.grid.get_type(pos.add(Vec(1, 0))) in ["-", "7", "J"]:
            directions.append(Vec(1, 0))
        if self.grid.get_type(pos.add(Vec(-1, 0))) in ["-", "F", "L"]:
            directions.append(Vec(-1, 0))
        if len(directions) != 2:
            raise Exception(f"Wrong number of directions! {directions}")
        self.searcher_a.pos = self.start_cell.pos
        self.searcher_b.pos = self.start_cell.pos
        self.searcher_a.move(directions[0])
        self.searcher_b.move(directions[1])

    def viz(self):
        # show(str(self.grid.location_to_cell))
        pass

State.lookup = {
    (Vec(1, 0),  "-"): Vec(1, 0),
    (Vec(-1, 0), "-"): Vec(-1, 0),

    (Vec(0, 1),  "|"): Vec(0, 1),
    (Vec(0, -1), "|"): Vec(0, -1),

    (Vec(0, 1), "L"): Vec(1, 0),
    (Vec(-1, 0), "L"): Vec(0, -1),

    (Vec(0, 1), "J"): Vec(-1, 0),
    (Vec(1, 0), "J"): Vec(0, -1),

    (Vec(0, -1), "7"): Vec(-1, 0),
    (Vec(1, 0), "7"): Vec(0, 1),

    (Vec(0, -1), "F"): Vec(1, 0),
    (Vec(-1, 0), "F"): Vec(0, 1),
}

def parse_line(state: State, line: str, y):
    for x, type in enumerate(line):
        cell = Cell(Vec(x, y), type)
        state.grid.add(Cell(Vec(x, y), type))
        if type == "S":
            state.start_cell = cell
    return state

def calculate(filename):
    state = State()
    every_line(state, filename, [parse_line])
    return state.find_midpoint()

pret("Trial: ", calculate("trial.txt"))
pret("Input: ", calculate("input.txt"))
