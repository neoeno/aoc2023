from dataclasses import dataclass, field
from utility.main import check, pret, every_line

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
class Column:
    spans: list[Span] = field(default_factory=list)
    room_length: int = 0

    def add(self, char, row):
        self.room_length += 1
        if len(self.spans) == 0:
            self.spans.append(Span(0, 0))
        if char == "O":
            self.spans[-1].rocks += 1
        elif char == "#":
            self.spans.append(Span(row + 1, 0))

    def calculate(self):
        return sum(span.calculate(self.room_length) for span in self.spans)

my_column = Column()
for r, c in enumerate(["O", "O", ".", "O", ".", "O", ".", ".", "#", "#"]):
    my_column.add(c, r)
check(my_column.calculate(), 34)
my_column = Column()
for r, c in enumerate([".", "O", ".", ".", ".", "#", "O", ".", ".", "O"]):
    my_column.add(c, r)
check(my_column.calculate(), 7 + 10)

@dataclass
class State:
    columns: dict[int, Column] = field(default_factory=dict)

    def add(self, col, row, char):
        if col not in self.columns:
            self.columns[col] = Column()
        self.columns[col].add(char, row)

    def calculate(self):
        return sum(col.calculate() for col in self.columns.values())

def parse_line(state, line, row):
    for col, char in enumerate(line):
        state.add(col, row, char)
    return state

def calculate(filename):
    state = State()
    every_line(state, filename, [parse_line])
    return state.calculate()

pret("Trial:", calculate("trial.txt"))
pret("Input:", calculate("input.txt"))
