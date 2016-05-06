from itertools import combinations_with_replacement
from sys import argv
import re


class RowCol:
    def __init__(self, rule, puzzle, num):
        self.rule = rule
        self.puzzle = puzzle
        self.num = num
        self.possible = [self.construct(false) for false in self.falses()]
        self.get_content()

        if len(self.possible) == 1:
            self.set_content(self.possible[0])
            self.possible = []

    def is_solved(self):
        return all(x is not None for x in self.get_content())

    def conforms(self, test):
        return all(b is None or a == b for a, b in zip(test, self.get_content()))

    def construct(self, spaces):
        perm = []
        for i in range(len(spaces) + len(self.rule)):
            fill = [False] * spaces[i // 2] if i % 2 == 0 else [True] * self.rule[i // 2]
            perm.extend(fill)
        return perm

    def falses(self):
        if self.rule == (0,):
            return [(len(self.get_content()), 0)]

        needed = len(self.get_content()) - (sum(self.rule) + len(self.rule) - 1)  # total - known
        spaces = len(self.rule) + 1

        if needed == 0:
            perm = tuple(0 for _ in range(spaces))
            yield perm[:1] + tuple(i + 1 for i in perm[1:-1]) + perm[-1:]
        else:
            matrix = [[0 for _ in range(spaces)] for _ in range(spaces)]
            for i in range(spaces):
                matrix[i][i] = 1
            for perm in combinations_with_replacement(matrix, needed):
                perm = tuple(sum(i) for i in zip(*perm))
                yield perm[:1] + tuple(i + 1 for i in perm[1:-1]) + perm[-1:]

    def fill(self):
        self.possible = [possible for possible in self.possible if self.conforms(possible)]
        if len(self.possible) == 0:
            return set()
        if len(self.possible) == 1:
            absolute = self.possible[0]
            self.possible = []
        else:
            absolute = []
            for x in zip(*self.possible):
                if len(set(x)) == 1:
                    absolute.append(x[0])
                else:
                    absolute.append(None)

        test = self.get_content()
        self.set_content(absolute)
        return set(i for i in range(len(absolute)) if test[i] is None and absolute[i] is not None)

    def get_content(self):
        if isinstance(self, Row):
            return self.puzzle.get_row(self.num)
        elif isinstance(self, Col):
            return self.puzzle.get_col(self.num)
        else:
            raise NotImplementedError

    def set_content(self, content):
        if isinstance(self, Row):
            self.puzzle.set_row(self.num, content)
        elif isinstance(self, Col):
            self.puzzle.set_col(self.num, content)
        else:
            raise NotImplementedError


class Row(RowCol):
    def get_content(self):
        return self.puzzle.get_row(self.num)

    def set_content(self, content):
        self.puzzle.set_row(self.num, content)


class Col(RowCol):
    def get_content(self):
        return self.puzzle.get_col(self.num)

    def set_content(self, content):
        self.puzzle.set_col(self.num, content)


class Nonogram:
    def __init__(self, rules):
        self.rows, self.cols = rules
        self.grid = [[None] * len(self.cols) for _ in range(len(self.rows))]
        self.rows = [Row(row, self, i) for i, row in enumerate(self.rows)]
        self.cols = [Col(col, self, i) for i, col in enumerate(self.cols)]

    def fill(self, rownotcol, target=None):
        collection = self.rows if rownotcol else self.cols
        if target is None:
            target = range(len(collection))
        affected = set()
        for i in target:
            affected.update(collection[i].fill())
        return affected

    def solve(self):
        rownotcol = True
        self.fill(not rownotcol)
        affected = {True: range(len(self.grid)), False: range(len(self.grid[0]))}
        old_grid = [row[:] for row in self.grid]
        while not self.is_solved():

            affected[not rownotcol] = self.fill(rownotcol, affected[rownotcol])
            rownotcol = not rownotcol
            if rownotcol:
                if old_grid == self.grid:
                    return
                old_grid = [row[:] for row in self.grid]

    def is_solved(self):
        return all(all(x is not None for x in row) for row in self.grid)

    def get_col(self, num):
        return [row[num] for row in self.grid]

    def get_row(self, num):
        return self.grid[num][:]

    def set_col(self, num, replace):
        if not len(self.grid) == len(replace):
            raise Exception("Invalid replace length")
        for i, e in enumerate(replace):
            self.grid[i][num] = e

    def set_row(self, num, replace):
        if not len(self.grid[num]) == len(replace):
            raise Exception("Invalid replace length")
        self.grid[num] = replace[:]

    def print_grid(self):
        tfn = "*.N"
        print('+' + '-' * len(self.cols) + '+')
        for row in self.grid:
            print('|' + ''.join(tfn[(True, False, None).index(i)] for i in row) + '|', end="")
            out = ""
            count = 0
            prev = row[0]
            for i in row:
                if i is prev:
                    count += 1
                else:
                    out += " " + tfn[(True, False, None).index(prev)] + str(count)
                    prev = i
                    count = 1
            out += " " + tfn[(True, False, None).index(prev)] + str(count)
            print(out)
        print('+' + '-' * len(self.cols) + '+')
        print("Solved" if self.is_solved() else "Not solved")


def parse(puzzle_file):
    separator = re.compile("-+")
    rule = re.compile("[0-9]+( +[0-9]+)*")
    puzzle = []

    with open(puzzle_file) as file:
        dimension = []
        for line in file:
            line = line.strip()
            match = rule.match(line)
            if match:
                group = match.group()
                group = tuple(int(i) for i in group.split(" ")) if not group == "0" else (0,)
                dimension.append(group)
            else:
                match = separator.match(line)
                if match:
                    puzzle.append(dimension)
                    dimension = []
                else:
                    continue
        if not dimension == []:
            puzzle.append(dimension)

    return puzzle


def solve(puzzle):
    if isinstance(puzzle, str):
        puzzle = Nonogram(parse(puzzle))
    else:
        puzzle = Nonogram(puzzle)
    puzzle.solve()
    puzzle.print_grid()


if __name__ == "__main__":
    if len(argv) > 1:
        solve(argv[1])
