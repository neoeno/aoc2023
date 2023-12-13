from dataclasses import dataclass, field
import time

from utility.main import check, every_line, hrange, pret

# ???#??.?#??.?

@dataclass
class Record:
    pattern: str
    spans: list[int]
    found: set[str] = field(default_factory=set)

    def count_possibles(self):
        # print(f"     PTTRN: {self.pattern} ({self._gaps_to_place()})")
        self._count_possibles(self.pattern, self._gaps_to_place(), self.spans)
        return len(self.found)

    def _count_possibles(self, pattern, dots_to_place, spans, stem = ""):
        # print(stem, dots_to_place, spans)
        if len(stem) == len(self.pattern):
            # print(f"GDD RESULT: {stem} ({dots_to_place})")
            self.found.add(stem)
            return 1
        count = 0
        for gap in range(dots_to_place, -1, -1):
            if len(spans) == 0 and gap == 0:
                continue
            grown = self._grow([gap], spans)
            if self._matches(pattern[0:len(grown)], grown):
                # print(f"   Y{gap}: '{grown}'")
                count += self._count_possibles(
                    pattern[len(grown):],
                    dots_to_place - gap,
                    spans[1:],
                    stem + grown
                )
            else:
                pass
        return count

    def _gaps_to_place(self):
        return len(self.pattern) - sum(self.spans) - len(self.spans) + 1

    def _matches(self, pattern: str, candidate: str):
        if pattern == candidate:
            return True
        if len(pattern) != len(candidate):
            return False
        for idx in hrange(0, len(pattern) - 1, len(pattern)):
            if pattern[idx] != "?" and pattern[idx] != candidate[idx]:
                return False
        return True

    def _grow(self, bins: list[int], spans: list[int]):
        assert len(bins) == 1
        if len(bins) == 0:
            return ""
        grown = "." * bins[0]
        if len(spans) > 0:
            grown += "#" * spans[0]
        if len(spans) > 1:
            grown += "."
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
        return sum(r.count_possibles() for r in self.records)


# #.#.### 1,1,3
# .#...#....###. 1,1,3
# .#.###.#.###### 1,3,1,6
# ####.#...#... 4,1,1
# #....######..#####. 1,6,5
# .###.##....# 3,2,1

def parse_line(state, line, _idx):
    halves = line.split(" ")
    pattern = halves[0]
    numbers = [int(numstr) for numstr in halves[1].split(",")]
    state.records.append(Record(pattern, numbers))
    return state

def calculate(filename):
    state = State()
    every_line(state, filename, [parse_line])
    return state.sum_counts()

pret("Trial: ", calculate("trial.txt"))
pret("Input: ", calculate("input.txt"))
# 8465 - too high
