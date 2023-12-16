from dataclasses import dataclass
import re

from utility.main import check, every_line, pret


@dataclass
class State:
    line: str = ""

    def sum_sequences(self):
        total = 0
        for chunk in re.finditer(r"[^,\s]+", self.line):
            total += self.calc_hash(chunk.group(0))
        return total

    def calc_hash(self, chunk: str):
        val = 0
        for char in chunk:
            val += ord(char)
            val *= 17
            val %= 256
        return val

my_state = State()
check(my_state.calc_hash("HASH"), 52)
check(my_state.calc_hash("rn=1"), 30)

def parse_line(state, line, idx):
    state.line = line

def calculate(filename):
    state = State()
    every_line(state, filename, [parse_line])
    return state.sum_sequences()

pret("Trial:", calculate("trial.txt"))
pret("Input:", calculate("input.txt"))
