from dataclasses import dataclass, field

from utility.main import check, every_line, hrange, pret


@dataclass(frozen=True)
class Vec:
    x: int
    y: int

    def add(self, other):
        return Vec(self.x + other.x, self.y + other.y)

    def mdist(self, other):
        return abs(self.x - other.x) + abs(self.y - other.y)

check(Vec(4, 0).mdist(Vec(9, 10)), 15)
check(Vec(9, 10).mdist(Vec(4, 0)), 15)

@dataclass(frozen=True)
class Galaxy:
    pos: Vec

@dataclass
class Space:
    x_gaps: list[int] = field(default_factory=list)
    y_gaps: list[int] = field(default_factory=list)
    x_conv: dict[int, int] = field(default_factory=dict)
    y_conv: dict[int, int] = field(default_factory=dict)
    max_x: int = 0
    max_y: int = 0

    def distance(self, a, b):
        if len(self.x_conv) == 0:
            self._calc_conv()
        return self._conv(a).mdist(self._conv(b))

    def _calc_conv(self):
        self.max_x = max(self.x_gaps)
        self.max_y = max(self.y_gaps)
        for x in hrange(0, max(self.x_gaps), max(self.x_gaps) + 1):
            self.x_conv[x] = len(list(n for n in self.x_gaps if n <= x))
        for y in hrange(0, max(self.y_gaps), max(self.y_gaps) + 1):
            self.y_conv[y] = len(list(n for n in self.y_gaps if n <= y))

    def _conv(self, a):
        x, y = a.x, a.y
        if x > self.max_x:
            x = self.x_conv[self.max_x]
        else:
            x = self.x_conv[x]
        if y > self.max_y:
            y = self.y_conv[self.max_y]
        else:
            y = self.y_conv[y]
        return a.add(Vec(x, y))

@dataclass
class State:
    space: Space = field(default_factory=Space)
    galaxies: list[Galaxy] = field(default_factory=list)
    width: int = 0
    found_xs: set[int] = field(default_factory=set)

    def galaxy_pairs(self):
        pairs = 0
        for a_idx, galaxy_a in enumerate(self.galaxies):
            for b_idx in range(a_idx + 1, len(self.galaxies)):
                yield (galaxy_a, self.galaxies[b_idx])
                pairs += 1

    def sum_distances(self):
        distances = 0
        for ga, gb in self.galaxy_pairs():
            distances += self.space.distance(ga.pos, gb.pos)
        return distances

def parse_line(state: State, line, y):
    state.width = len(line)
    found_galaxy = False
    for x, c in enumerate(line):
        if c == "#":
            state.galaxies.append(Galaxy(Vec(x, y)))
            state.found_xs.add(x)
            found_galaxy = True
    if found_galaxy == False:
        state.space.y_gaps.append(y)
    return state

def calculate(filename):
    state = State()
    every_line(state, filename, [parse_line])
    for x in hrange(0, state.width - 1, state.width):
        if x not in state.found_xs:
            state.space.x_gaps.append(x)
    return state.sum_distances()

pret("Trial:", calculate("trial.txt"))
pret("Input:", calculate("input.txt"))
