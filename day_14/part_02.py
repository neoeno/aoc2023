from dataclasses import dataclass, field
from time import sleep
from utility.main import check, pret, every_line, show

@dataclass
class Span:
    start: int
    rocks: int

    def calculate(self, room_length: int) -> int:
        edge = room_length - self.start
        return int(-0.5*self.rocks**2 + self.rocks*edge + 0.5 * self.rocks)

my_span = Span(0, 4)
check(my_span.calculate(10), 34)
my_span = Span(6, 2)
check(my_span.calculate(10), 7)

@dataclass
class Pipe:
    spans: list[Span] = field(default_factory=list)
    room_length: int = 0
    blocks: set[int] = field(default_factory=set)

    def add(self, char, row):
        self.room_length += 1
        if len(self.spans) == 0:
            self.spans.append(Span(0, 0))
        if char == "O":
            self.spans[-1].rocks += 1
        elif char == "#":
            self.blocks.add(row)
            self.spans.append(Span(row + 1, 0))

    def get_cell(self, n):
        if n in self.blocks:
            return "#"
        right_span = self.spans[-1]
        for idx, span in enumerate(self.spans):
            if span.start > n:
                right_span = self.spans[idx - 1]
                break
        if n in range(right_span.start, right_span.start + right_span.rocks):
            return "O"
        else:
            return "."

    def get_cell_from_end(self, n):
        return self.get_cell(self.room_length - n - 1)

    def calculate(self):
        return sum(span.calculate(self.room_length) for span in self.spans)

    def count(self):
        return sum(span.rocks for span in self.spans)

    def __repr__(self):
        return "".join(self.get_cell(n) for n in range(0, self.room_length))


my_pipe = Pipe()
for r, c in enumerate(["O", "O", ".", "O", ".", "O", ".", ".", "#", "#"]):
    my_pipe.add(c, r)
check(my_pipe.calculate(), 34)
my_pipe = Pipe()
for r, c in enumerate([".", "O", ".", ".", ".", "#", "O", ".", ".", "O"]):
    my_pipe.add(c, r)
check(my_pipe.calculate(), 7 + 10)
check(my_pipe.get_cell(0), "O")
check(my_pipe.get_cell(1), ".")
check(my_pipe.get_cell(2), ".")
check(my_pipe.get_cell(3), ".")
check(my_pipe.get_cell(4), ".")
check(my_pipe.get_cell(5), "#")
check(my_pipe.get_cell(6), "O")
check(my_pipe.get_cell(7), "O")
check(my_pipe.get_cell(8), ".")
check(my_pipe.get_cell(9), ".")
my_pipe = Pipe()
for r, c in enumerate([".", ".", ".", ".", ".", "#", "O", ".", ".", "O"]):
    my_pipe.add(c, r)
check(my_pipe.get_cell(0), ".")
check(my_pipe.get_cell(1), ".")
check(my_pipe.get_cell(2), ".")
check(my_pipe.get_cell(3), ".")
check(my_pipe.get_cell(4), ".")
check(my_pipe.get_cell(5), "#")
check(my_pipe.get_cell(6), "O")
check(my_pipe.get_cell(7), "O")
check(my_pipe.get_cell(8), ".")
check(my_pipe.get_cell(9), ".")
check(my_pipe.get_cell_from_end(0), ".")
check(my_pipe.get_cell_from_end(1), ".")
check(my_pipe.get_cell_from_end(2), "O")
check(my_pipe.get_cell_from_end(3), "O")
check(my_pipe.get_cell_from_end(4), "#")
check(my_pipe.get_cell_from_end(5), ".")
check(my_pipe.get_cell_from_end(6), ".")
check(my_pipe.get_cell_from_end(7), ".")
check(my_pipe.get_cell_from_end(8), ".")
check(my_pipe.get_cell_from_end(9), ".")

@dataclass
class State:
    pipes: dict[int, Pipe] = field(default_factory=dict)
    width: int = 0
    height: int = 0
    cycles: int = 0

    def cycle(self):
        self.roll_north()
        self.roll_west()
        self.roll_south()
        self.roll_east()
        self.cycles += 1
        seq = [93725, 93718, 93701, 93698, 93694, 93688, 93683, 93684, 93688, 93678, 93686, 93720, 93740, 93730, 93731, 93738, 93746, 93751, 93743, 93728, 93730, 93731, 93735, 93736, 93724, 93713]
        expected = seq[(self.cycles + 11) % len(seq)]
        # expected = [69, 69, 65, 64, 65, 63, 68][(self.cycles + 4) % 7]
        print(self.cycles, self.north_value(), expected, self.north_value() == expected)
        # self.viz(f"Rolled East {self.cycles}", False, True, True)

    def north_value(self):
        total = 0
        for pipen in self.pipes.keys():
            total += self.pipes[pipen].count() * (pipen + 1)
        return total


    def add_and_roll_north(self, col, row, char):
        if col not in self.pipes:
            self.pipes[col] = Pipe()
        self.pipes[col].add(char, row)

    def roll_north(self):
        new_pipes = {}
        room_length = self.pipes[0].room_length
        for new_pipen in range(0, room_length):
            new_pipes[new_pipen] = Pipe()
            for pipen in sorted(self.pipes.keys(), reverse=True):
                pipe = self.pipes[pipen]
                new_pipes[new_pipen].add(pipe.get_cell(new_pipen), room_length - pipen - 1)
        self.pipes = new_pipes
        self.width, self.height = self.height, self.width

    def roll_west(self):
        new_pipes = {}
        room_length = self.pipes[0].room_length
        for new_pipen in range(0, room_length):
            new_pipes[new_pipen] = Pipe()
            for pipen in sorted(self.pipes.keys(), reverse=True):
                pipe = self.pipes[pipen]
                new_pipes[new_pipen].add(pipe.get_cell(new_pipen), room_length - pipen - 1)
        self.pipes = new_pipes
        self.width, self.height = self.height, self.width

    def roll_west_init(self):
        new_pipes = {}
        room_length = self.pipes[0].room_length
        for new_pipen in range(0, room_length):
            new_pipes[new_pipen] = Pipe()
            for pipen in sorted(self.pipes.keys()):
                pipe = self.pipes[pipen]
                new_pipes[new_pipen].add(pipe.get_cell(new_pipen), pipen)
        self.pipes = new_pipes
        self.width, self.height = self.height, self.width

    def roll_south(self):
        new_pipes = {}
        room_length = self.pipes[0].room_length
        for new_pipen in range(0, room_length):
            new_pipes[new_pipen] = Pipe()
            for pipen in sorted(self.pipes.keys(), reverse=True):
                pipe = self.pipes[pipen]
                new_pipes[new_pipen].add(pipe.get_cell(new_pipen), room_length - pipen - 1)
        self.pipes = new_pipes
        self.width, self.height = self.height, self.width

    def roll_east(self):
        new_pipes = {}
        room_length = self.pipes[0].room_length
        for new_pipen in range(0, room_length):
            new_pipes[new_pipen] = Pipe()
            for pipen in sorted(self.pipes.keys(), reverse=True):
                pipe = self.pipes[pipen]
                new_pipes[new_pipen].add(pipe.get_cell(new_pipen), room_length - pipen - 1)
        self.pipes = new_pipes
        self.width, self.height = self.height, self.width

    def calculate(self):
        return sum(col.calculate() for col in self.pipes.values())

    def viz(self, label, rotate = False, fliph = False, flipv = False):
        grid = []
        for rown in range(0, self.pipes[0].room_length):
            row = []
            for pipen in sorted(self.pipes.keys(), reverse=fliph):
                if rotate:
                    row.append(self.pipes[pipen].get_cell(rown))
                else:
                    row.append(self.pipes[rown].get_cell(pipen))
            grid.append("".join(row))
        if flipv:
            grid = reversed(grid)
        show("\n".join([label, *grid]), clear=True)

def parse_line(state: State, line: str, row: int):
    for col, char in enumerate(line):
        state.add_and_roll_north(col, row, char)
    state.height = row
    state.width = len(line)
    return state

def calculate(filename):
    state = State()
    every_line(state, filename, [parse_line])
    state.viz("Rolled North", True)
    state.roll_west_init()
    state.roll_south()
    state.roll_east()
    state.cycles += 1
    # state.viz(f"Rolled East {state.cycles}", False, True, True)
    print(state.north_value())

    while True:
        state.cycle()
        # sleep(0.1)

# pret("Trial:", calculate("trial.txt"))
pret("Input:", calculate("input.txt"))
