from dataclasses import dataclass, field
from math import floor
import time

from utility.main import check, every_line, hrange, pret

# ???#??.?#??.?

@dataclass
class Record:
    pattern: str
    spans: list[int]
    checks: int = 0
    cache: dict[str, int] = field(default_factory=dict)

    def count_possibles(self):
        return self._count_possibles(self.pattern, self._gaps_to_place(), self.spans)

    def _count_possibles(self, pattern, dots_to_place, spans, stem = "", gaps = None):
        if gaps is None:
            gaps = []
        key = str((pattern, dots_to_place, spans, stem, len(gaps)))
        if len(gaps) == len(self.spans) + 1:
            if dots_to_place > 0:
                self.cache[key] = 0
                return 0
            self.cache[key] = 1
            return 1
        if key in self.cache:
            return self.cache[key]
        count = 0
        max_dots = min(pattern.find("#"), dots_to_place)
        if max_dots == -1:
            max_dots = dots_to_place
        for gap in range(max_dots, -1, -1):
            if self._gmatches(pattern, gap, spans):
                growlen = self._growlen(gap, spans)
                count += self._count_possibles(
                    pattern[growlen:],
                    dots_to_place - gap,
                    spans[1:],
                    stem + "",
                    [*gaps, gap]
                )
        self.cache[key] = count
        return count

    def _gaps_to_place(self):
        return len(self.pattern) - sum(self.spans) - len(self.spans) + 1

    def _matches(self, pattern: str, candidate: str):
        self.checks += 1
        if pattern == candidate:
            return True
        if len(pattern) != len(candidate):
            return False
        for idx in hrange(0, len(pattern) - 1, len(pattern)):
            if pattern[idx] != "?" and pattern[idx] != candidate[idx]:
                return False
        return True

    def _gmatches(self, pattern, gap, spans):
        if len(spans) == 0:
           return all(c in ".?" for c in pattern[0:gap])
        elif all(c in ".?" for c in pattern[0:gap]):
            if all(c in "#?" for c in pattern[gap:gap+spans[0]]):
                if len(spans) == 1 or pattern[gap+spans[0]] in "?.":
                    return True
        return False

    def _grow(self, gap: int, spans: list[int]):
        grown = "." * gap
        if len(spans) > 0:
            grown += "#" * spans[0]
        if len(spans) > 1:
            grown += "."
        return grown

    def _growlen(self, gap: int, spans: list[int]):
        grown = 1 * gap
        if len(spans) > 0:
            grown += 1 * spans[0]
        if len(spans) > 1:
            grown += 1
        return grown

# my_record = Record("?###????????", [3, 2, 1])
# check(my_record._matches("?.?", "#.#"), True)
# check(my_record._matches("?.?", "###"), False)
# # check(my_record._grow([], [3, 2, 1]), "")
# # check(my_record._grow([2], [3, 2, 1]), "..###.")
# # check(my_record._grow([2, 1], [3, 2, 1]), "..###..##.")
# # check(my_record._grow([2, 1, 3], [3, 2, 1]), "..###..##....#")
# # check(my_record._grow([2, 1, 3, 4], [3, 2, 1]), "..###..##....#....")
# check(my_record._gaps_to_place(), 4)
# check(my_record.count_possibles(), 10)

@dataclass
class State:
    records: list[Record] = field(default_factory=list)

    def sum_counts(self):
        total = 0
        for idx, r in enumerate(self.records):
            print(f"Progress: {floor((idx/len(self.records)*100))}%")
            total += r.count_possibles()
        return total


def parse_line(state, line, _idx):
    halves = line.split(" ")
    pattern = halves[0] + "?" + halves[0] + "?" + halves[0] + "?" + halves[0] + "?" + halves[0]
    numbers = [int(numstr) for numstr in halves[1].split(",")] * 5
    # pattern = halves[0]
    # numbers = [int(numstr) for numstr in halves[1].split(",")]
    state.records.append(Record(pattern, numbers))
    return state

def calculate(filename):
    state = State()
    every_line(state, filename, [parse_line])
    return state.sum_counts()

pret("Trial: ", calculate("trial.txt"))
pret("Input: ", calculate("input.txt"))
