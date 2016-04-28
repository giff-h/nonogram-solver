from itertools import combinations_with_replacement


class Nonogram:
    def __init__(self, rules):
        self.rows, self.cols = rules
        self.grid = [[None for _ in range(len(self.cols))] for _ in range(len(self.rows))]

    @staticmethod
    def conforms(test, control):
        """
        Returns True if all the non-None elements in control match their position in test

        :param test: The potential permutation. Should be all non-None.
        :param control: The control to test against. Should be the pre-existing array.
        :return: Boolean.
        """

        return all(b is None or a == b for a, b in zip(test, control))

    @staticmethod
    def construct(spaces, rule):
        """
        Builds the array of Trues and Falses from the rule and permutation of spaces. The total sum of spaces and
        rule should be the length of the resulting array.

        :param spaces: The number of Falses to go in the appropriate places among the Trues.
        :param rule: The original rule associated with the array. This corresponds to the Trues.
        :return: The resulting list of Trues and Falses
        """

        perm = []
        for i in range(len(spaces) + len(rule)):
            fill = [False] * spaces[i // 2] if i % 2 == 0 else [True] * rule[i // 2]
            perm.extend(fill)
        return perm

    @staticmethod
    def falses(spaces, needed):
        """
        A generator for the permutations of spaces to be passed through to construct. The resulting sum of each
        permutation will be more than the value of needed, because this adds the expected necessary False between the
        rule groups.

        :param spaces: The number of groups necessary in each permutation. Should be the number of rule groups plus one.
        :param needed: The total number of Falses needed besides the normal False between the rule groups.
        :return: The generator of permutations.
        """

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

    @staticmethod
    def solve(rules):
        """
        The one-stop method for soling a puzzle. It takes the rules, builds and solves the puzzles, and prints the
        resulting grid.

        :param rules: An iterable with 2 iterables, row and column respectively, each iterable has tuples which are the
        rules.
        """

        puzzle = Nonogram(rules)
        row = True
        puzzle.fills(not row)
        affected = {True: range(len(puzzle.grid)), False: range(len(puzzle.grid[0]))}
        old_grid = [row[:] for row in puzzle.grid]
        while not puzzle.is_solved():
            affected[not row] = puzzle.fills(row, affected[row])
            row = not row
            if row:
                if old_grid == puzzle.grid:
                    break
                old_grid = [row[:] for row in puzzle.grid]
        puzzle.print_grid()

    def fill(self, num, row=True):
        """
        The meat of this whole operation. Fills the identified row or column as much as it can given all possible
        permutations from the information currently available, the rule and already filled/emptied areas.

        :param num: Integer. The row or column id
        :param row: Boolean. Whether it's a row or column
        :return: A set of all the perpendicular elements affected.
        """

        # compare is what already exists, to later drop anything that doesn't conform to preexisting True and False
        compare = self.get_rowcol(num, row)
        rule = self.rows[num] if row else self.cols[num]  # The rule that appears next to the row or column
        known = sum(rule) + len(rule) - 1  # The minimum size the rule would take
        total = len(compare)  # If known == total then there is only one solution
        assert total >= known  # I dare you to find somewhere in the universe this doesn't apply

        possible = []  # The set of possibilities by the rules. Drop all that don't fit compare, then transpose
        for perm in Nonogram.falses(len(rule) + 1, total - known):
            perm = Nonogram.construct(perm, rule)
            if Nonogram.conforms(perm, compare):
                possible.append(perm)

        if len(possible) == 0:
            return []
        elif len(possible) == 1:
            self.set_rowcol(num, possible[0], row)
            affected = range(len(possible[0]))
        else:
            absolute = []
            for x in zip(*possible):
                if len(set(x)) == 1:
                    absolute.append(x[0])
                else:
                    absolute.append(None)

            self.set_rowcol(num, absolute, row)
            affected = [i for i, x in enumerate(absolute) if x is not None and not x == compare[i]]

        return affected

    def fills(self, row=True, affect=None):
        """
        The master solver method. Will parse all the rows or columns for any that still have a None (unsolved), and
        use fill to solve them.

        It will take the sets returned by each instance of fill and use them to simplify what to fill next.

        :param row: Boolean. Whether it's a row or column
        :param affect: An iterable of the rows or columns to affect. It defaults to all the rows or columns.
        :return: The affected areas, as a sorted list
        """

        if affect is None:
            affect = range(len(self.grid if row else self.grid[0]))
        affected = set()
        for i in affect:
            rowcol = self.get_rowcol(i, row)
            if any(x is None for x in rowcol):
                affected = affected.union(self.fill(i, row))
        return affected

    def is_solved(self):
        """
        Determines if the puzzle is solved, by searching for Nones.

        :return: Boolean.
        """

        return all(all(x is not None for x in row) for row in self.grid)

    def get_rowcol(self, num, row=True):
        """
        Gets a copy of the identified row or column. Modifying it will not affect the puzzle.

        :param num: Integer. The row or column id
        :param row: Boolean. Whether it's a row or column
        :return: A list of Trues, Falses, or Nones
        """

        return self.grid[num][:] if row else [row[num] for row in self.grid]

    def set_rowcol(self, num, replace, row=False):
        """
        Sets the identified row or column to the given list

        :param num: Integer. The row or column id
        :param replace: The list to replace into the grid
        :param row: Boolean. Whether it's a row or column
        """

        if row:
            if not len(self.grid[num]) == len(replace):
                raise Exception("Invalid replace length")
            self.grid[num] = replace[:]
        else:
            if not len(self.grid) == len(replace):
                raise Exception("Invalid replace length")
            for i, e in enumerate(replace):
                self.grid[i][num] = e

    def print_grid(self):
        """
        Pretty prints the grid.

        Example: 5x5
        +-----+
        |**.**|
        |*...*|
        |..*..|
        |*...*|
        |.***.|
        +-----+

        * is filled
        . is empty
        N is unknown. Creating a Nonogram then immediately printing it will be just this.
        """

        print('+' + '-' * len(self.cols) + '+')
        for row in self.grid:
            print('|' + ''.join("*.N"[(True, False, None).index(i)] for i in row) + '|')
        print('+' + '-' * len(self.cols) + '+')

Nonogram.solve([[(1, 5, 2), (2, 2, 3, 1), (6, 1, 3), (3, 1, 1, 1, 2, 3, 1), (2, 3, 2, 1, 1, 2), (2, 2, 1, 1, 4), (2, 3, 5, 4), (2, 2, 1, 1, 1, 2, 4), (2, 3, 2, 2, 4), (3, 3, 2), (1, 3, 1, 1), (6, 7), (3, 1, 2, 1, 1), (2, 4, 4, 1, 1), (2, 1, 5, 3, 2)],
                [(6,),(8,),(4,2,2),(1,4,1,3),(8,1),(1,1,1,1,1,2),(1,1,2,1,2),(2,3),(1,1,1,2),(1,1,1,1,1),(1,1,1,1,1,1),(1,1,3,1,2),(2,4,1,3),(1,8),(2,7,2),(1,3,1,1,1),(4,4,2,1),(1,5,3),(6,1,1),(6,5)]])
