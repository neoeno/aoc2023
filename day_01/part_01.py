from utility.main import check, every_line, hrange, pret, show


def is_digit_at_point(line, idx):
    return line[idx].isdigit()

check(is_digit_at_point("1abc2", 0), True)
check(is_digit_at_point("1abc2", 1), False)
check(is_digit_at_point("1abc2", 4), True)

def find_first_digit(line):
    for idx, char in enumerate(line):
        if is_digit_at_point(line, idx):
            return char

check(find_first_digit("1abc2"), "1")
check(find_first_digit("pqr3stu8vwx"), "3")

def find_last_digit(line):
    for idx in range(len(line) - 1, -1, -1):
        if is_digit_at_point(line, idx):
            return line[idx]

check(find_last_digit("1abc2"), "2")
check(find_last_digit("pqr3stu8vwx"), "8")
check(find_last_digit("1abc"), "1")

def make_calibration_value(a, b):
    return int(f"{a}{b}")

check(make_calibration_value("3", "2"), 32)

add_calibration_values = sum

def calculate_line(line):
    return make_calibration_value(
        find_first_digit(line),
        find_last_digit(line))

check(calculate_line("1abc2"), 12)
check(calculate_line("pqr3stu8vwx"), 38)
check(calculate_line("1abc"), 11)

def calculate(filename):
    values = []
    with open(filename) as f:
        for line in f:
            values.append(calculate_line(line))
    return add_calibration_values(values)

check(pret("Trial result: ", calculate("trial.txt")), 142)
pret("Real result: ", calculate("input.txt"))
# 13:12

