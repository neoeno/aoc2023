from dataclasses import dataclass, field
from time import sleep

from utility.main import check, every_line, pret, show


@dataclass(frozen=True)
class Vec:
    x: int
    y: int

    def add(self, other):
        return Vec(self.x + other.x, self.y + other.y)

GOING_RIGHT = Vec(1, 0)
GOING_LEFT = Vec(-1, 0)
GOING_UP = Vec(0, -1)
GOING_DOWN = Vec(0, 1)

@dataclass(frozen=True)
class Beam:
    pos: Vec
    direction: Vec

@dataclass
class DiverterBackslash:
    pos: Vec

    def divert(self, beam: Beam) -> set[Beam]:
        if beam.direction == GOING_RIGHT:
            return {Beam(beam.pos.add(GOING_DOWN), GOING_DOWN)}
        elif beam.direction == GOING_LEFT:
            return {Beam(beam.pos.add(GOING_UP), GOING_UP)}
        elif beam.direction == GOING_DOWN:
            return {Beam(beam.pos.add(GOING_RIGHT), GOING_RIGHT)}
        elif beam.direction == GOING_UP:
            return {Beam(beam.pos.add(GOING_LEFT), GOING_LEFT)}
        else:
            raise Exception("Invalid direction!")

    def __repr__(self):
        return "\\"

d = DiverterBackslash(Vec(10, 10))
check(d.divert(Beam(d.pos, GOING_RIGHT)), {Beam(d.pos.add(GOING_DOWN), GOING_DOWN)})
check(d.divert(Beam(d.pos, GOING_LEFT)), {Beam(d.pos.add(GOING_UP), GOING_UP)})
check(d.divert(Beam(d.pos, GOING_DOWN)), {Beam(d.pos.add(GOING_RIGHT), GOING_RIGHT)})
check(d.divert(Beam(d.pos, GOING_UP)), {Beam(d.pos.add(GOING_LEFT), GOING_LEFT)})

@dataclass
class DiverterForwardslash:
    pos: Vec

    def divert(self, beam: Beam) -> set[Beam]:
        if beam.direction == GOING_RIGHT:
            return {Beam(beam.pos.add(GOING_UP), GOING_UP)}
        elif beam.direction == GOING_LEFT:
            return {Beam(beam.pos.add(GOING_DOWN), GOING_DOWN)}
        elif beam.direction == GOING_DOWN:
            return {Beam(beam.pos.add(GOING_LEFT), GOING_LEFT)}
        elif beam.direction == GOING_UP:
            return {Beam(beam.pos.add(GOING_RIGHT), GOING_RIGHT)}
        else:
            raise Exception("Invalid direction!")

    def __repr__(self):
        return "/"

d = DiverterForwardslash(Vec(10, 10))
check(d.divert(Beam(d.pos, GOING_RIGHT)), {Beam(d.pos.add(GOING_UP), GOING_UP)})
check(d.divert(Beam(d.pos, GOING_LEFT)), {Beam(d.pos.add(GOING_DOWN), GOING_DOWN)})
check(d.divert(Beam(d.pos, GOING_DOWN)), {Beam(d.pos.add(GOING_LEFT), GOING_LEFT)})
check(d.divert(Beam(d.pos, GOING_UP)), {Beam(d.pos.add(GOING_RIGHT), GOING_RIGHT)})


@dataclass
class DiverterPipe:
    pos: Vec

    def divert(self, beam: Beam) -> set[Beam]:
        if beam.direction == GOING_DOWN or beam.direction == GOING_UP:
            return {Beam(beam.pos.add(beam.direction), beam.direction)}
        elif beam.direction == GOING_LEFT or beam.direction == GOING_RIGHT:
            return {
                Beam(beam.pos.add(GOING_UP), GOING_UP),
                Beam(beam.pos.add(GOING_DOWN), GOING_DOWN),
            }
        else:
            raise Exception("Invalid direction!")

    def __repr__(self):
        return "|"

d = DiverterPipe(Vec(10, 10))
check(d.divert(Beam(d.pos, GOING_RIGHT)), {
    Beam(d.pos.add(GOING_UP), GOING_UP),
    Beam(d.pos.add(GOING_DOWN), GOING_DOWN)
})
check(d.divert(Beam(d.pos, GOING_LEFT)), {
    Beam(d.pos.add(GOING_UP), GOING_UP),
    Beam(d.pos.add(GOING_DOWN), GOING_DOWN)
})
check(d.divert(Beam(d.pos, GOING_DOWN)), {
    Beam(d.pos.add(GOING_DOWN), GOING_DOWN)
})
check(d.divert(Beam(d.pos, GOING_UP)), {
    Beam(d.pos.add(GOING_UP), GOING_UP)
})


@dataclass
class DiverterHyphen:
    pos: Vec

    def divert(self, beam: Beam) -> set[Beam]:
        if beam.direction == GOING_LEFT or beam.direction == GOING_RIGHT:
            return {Beam(beam.pos.add(beam.direction), beam.direction)}
        elif beam.direction == GOING_UP or beam.direction == GOING_DOWN:
            return {
                Beam(beam.pos.add(GOING_LEFT), GOING_LEFT),
                Beam(beam.pos.add(GOING_RIGHT), GOING_RIGHT),
            }
        else:
            raise Exception("Invalid direction!")

    def __repr__(self):
        return "-"

d = DiverterHyphen(Vec(10, 10))
check(d.divert(Beam(d.pos, GOING_UP)), {
    Beam(d.pos.add(GOING_LEFT), GOING_LEFT),
    Beam(d.pos.add(GOING_RIGHT), GOING_RIGHT)
})
check(d.divert(Beam(d.pos, GOING_DOWN)), {
    Beam(d.pos.add(GOING_LEFT), GOING_LEFT),
    Beam(d.pos.add(GOING_RIGHT), GOING_RIGHT)
})
check(d.divert(Beam(d.pos, GOING_LEFT)), {
    Beam(d.pos.add(GOING_LEFT), GOING_LEFT)
})
check(d.divert(Beam(d.pos, GOING_RIGHT)), {
    Beam(d.pos.add(GOING_RIGHT), GOING_RIGHT)
})

type Diverter = DiverterBackslash | DiverterForwardslash | DiverterHyphen | DiverterPipe

@dataclass
class State:
    start_beam: Beam = field(default=Beam(Vec(0, 0), GOING_RIGHT))
    beams: set[Beam] = field(default_factory=set)
    seen_beams: set[Beam] = field(default_factory=set)
    visited: set[Vec] = field(default_factory=set)
    diverters: dict[Vec, Diverter] = field(default_factory=dict)
    width: int = 0
    height: int = 0

    def process(self):
        self.beams.add(self.start_beam)
        while len(self.beams) > 0:
            beam = self.beams.pop()
            self.seen_beams.add(beam)
            if self.off_screen(beam.pos):
                continue
            new_beams = set()
            self.visited.add(beam.pos)
            if beam.pos in self.diverters:
                diverter = self.diverters[beam.pos]
                new_beams.update(diverter.divert(beam))
            else:
                new_beams.add(Beam(beam.pos.add(beam.direction), beam.direction))
            novel_beams = set()
            for beam in new_beams:
                if beam not in self.seen_beams:
                    novel_beams.add(beam)
            self.beams.update(novel_beams)

    def viz(self):
        grid = []
        for y in range(0, self.height):
            row = []
            for x in range(0, self.width):
                pos = Vec(x, y)
                if pos in (beam.pos for beam in self.beams):
                    row.append("*")
                elif pos in self.diverters:
                    row.append(str(self.diverters[pos]))
                elif pos in self.visited:
                    row.append("#")
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

    def reset(self):
        self.start_beam = Beam(Vec(0, 0), GOING_RIGHT)
        self.beams = set()
        self.seen_beams = set()
        self.visited = set()

my_state = State()
my_state.width = 5
my_state.height = 10
check(my_state.off_screen(Vec(-1, 0)), True)
check(my_state.off_screen(Vec(0, -1)), True)
check(my_state.off_screen(Vec(0, 0)), False)
check(my_state.off_screen(Vec(1, 0)), False)
check(my_state.off_screen(Vec(2, 0)), False)
check(my_state.off_screen(Vec(3, 0)), False)
check(my_state.off_screen(Vec(4, 0)), False)
check(my_state.off_screen(Vec(5, 0)), True)

def possible_beams(width: int, height: int):
    for y in range(0, height):
        yield Beam(Vec(0, y), GOING_RIGHT)
        yield Beam(Vec(width - 1, y), GOING_LEFT)
    for x in range(0, width):
        yield Beam(Vec(x, 0), GOING_DOWN)
        yield Beam(Vec(x, height - 1), GOING_UP)

check(set(possible_beams(3, 3)), {
    Beam(Vec(0, 0), GOING_RIGHT),
    Beam(Vec(0, 1), GOING_RIGHT),
    Beam(Vec(0, 2), GOING_RIGHT),
    Beam(Vec(0, 0), GOING_DOWN),
    Beam(Vec(1, 0), GOING_DOWN),
    Beam(Vec(2, 0), GOING_DOWN),
    Beam(Vec(0, 2), GOING_UP),
    Beam(Vec(1, 2), GOING_UP),
    Beam(Vec(2, 2), GOING_UP),
    Beam(Vec(2, 2), GOING_LEFT),
    Beam(Vec(2, 1), GOING_LEFT),
    Beam(Vec(2, 0), GOING_LEFT),
})

def parse_line(state: State, line: str, y: int) -> State:
    state.height = y + 1
    state.width = len(line)
    for x, char in enumerate(line):
        pos = Vec(x, y)
        if char == "/":
            state.diverters[pos] = DiverterForwardslash(pos)
        elif char == "\\":
            state.diverters[pos] = DiverterBackslash(pos)
        elif char == "-":
            state.diverters[pos] = DiverterHyphen(pos)
        elif char == "|":
            state.diverters[pos] = DiverterPipe(pos)
    return state

def calculate(filename):
    state = State()
    state = every_line(state, filename, [parse_line])
    state.viz()
    max_tiles = 0
    for beam in possible_beams(state.width, state.height):
        state.reset()
        state.start_beam = beam
        state.process()
        max_tiles = max(len(state.visited), max_tiles)
    return max_tiles

pret("Trial", calculate("trial.txt"))
pret("Input", calculate("input.txt"))
