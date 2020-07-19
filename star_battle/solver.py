import copy
from functools import reduce
import itertools
import time

from .board import bcolors


class Solution:
    def __init__(self, board, data=None):
        self._board = board
        self._data = data or [[None] * self._board.size for _ in range(self._board.size)]

    def copy(self):
        return type(self)(self._board, copy.deepcopy(self._data))

    def __getitem__(self, i):
        return self._data[i]

    def __iter__(self):
        return iter(self._data)

    @property
    def size(self):
        return self._board.size

    @property
    def stars(self):
        return self._board.stars

    @property
    def cell_index_iter(self):
        return self._board.cell_index_iter

    def _indices_with_value(self, value, area=None):
        cells = area or self.cell_index_iter
        return [(i, j) for i, j in cells if self[i][j] is value]

    def get_star_cells(self, **kwargs):
        return self._indices_with_value(True, **kwargs)

    def false_cells(self, **kwargs):
        return self._indices_with_value(False, **kwargs)

    def unknown_cells(self, **kwargs):
        return self._indices_with_value(None, **kwargs)

    def count_stars(self, **kwargs):
        return len(self.get_star_cells(**kwargs))

    def count_false(self, **kwargs):
        return len(self.false_cells(**kwargs))

    def count_unknown(self, **kwargs):
        return len(self.unknown_cells(**kwargs))

    def to_set(self):
        return frozenset(self.get_star_cells())

    def update_from_set(self, soln_set):
        for i, j in soln_set:
            self[i][j] = True

        for i, j in self.cell_index_iter:
            if not self.can_place_star(i, j):
                self[i][j] = False

    def can_place_star(self, row, col):
        """ Check if row,col can contain a star based board / running solution """

        # check neighbors (no start can neighbor another)
        for i, j in itertools.product(range(-1, 2), range(-1, 2)):
            r = row + i
            c = col + j

            if (i == 0 and j == 0) or not self._board.is_valid_cell(r, c):
                continue

            if self[r][c]:
                return False

        # check counts for areas, rows, cols

        # determine if we need to add one based on whether the currect cell has a star already
        add = 0 if self[row][col] else 1

        sol_sum = lambda it: sum(map(bool, it))

        return all(
            count + add <= self.stars
            for count in (
                sol_sum(self[row]),  # stars in the row
                sol_sum(self[i][col] for i in range(self.size)),  # stars in the column
                sol_sum(
                    self[i][j] for i, j in self._board.area_for_cell(row, col)
                ),  # stars in the area
            )
        )

    def verify(self):
        # check number of stars
        if not sum(sum(row) for row in self) == self._board.stars * self._board.size:
            return False

        for i, j in self.cell_index_iter:
            if self[i][j] and not self.can_place_star(i, j):
                return False

        return True


# Solve helpers


def solve_area(board, area, solution=None):
    """ Get solutions for a certain area given a working solution """

    solution = solution or Solution(board)
    ret = set()

    for i, j in area:
        if solution[i][j] is None:
            options = [False]
            if solution.can_place_star(i, j):
                options.append(True)

            for v in options:
                solution[i][j] = v
                ret.update(solve_area(board, area, solution))
                solution[i][j] = None

    if solution.count_unknown(area=area) == 0 and solution.count_stars(area=area) == board.stars:
        ret.add(solution.to_set())

    return ret


def solve_fully_defined_areas(board, solution=None):
    solution = solution or Solution(board)

    ordered_areas = list(sorted(board.areas, key=len))

    already_revisited = set()
    # find all fully defined areas and merge the solutions
    while len(ordered_areas):
        area = ordered_areas.pop(0)

        # skip areas with too many cells undefined
        if solution.count_unknown(area=area) > 6:
            continue

        solns = solve_area(board, area, solution)

        if len(solns) > 1:
            if area not in already_revisited:
                # let's come back to this
                ordered_areas.append(area)
                already_revisited.add(area)

            # look for cells that are eliminated by all possible solutions
            falseys = None
            for soln in solns:
                tmp_soln = solution.copy()
                tmp_soln.update_from_set(soln)

                if falseys is None:
                    falseys = set(tmp_soln.false_cells())
                else:
                    falseys.intersection_update(tmp_soln.false_cells())

            for i, j in falseys:
                solution[i][j] = False

            # keep cells that are stars in every solution
            s = solns.pop()
            common_cells = reduce(lambda a, b: a.intersection(b), solns, s)
            if len(common_cells):
                solution.update_from_set(common_cells)

        else:
            # something we revisted became determined, reset revisit history
            if area in already_revisited:
                already_revisited.clear()

            solution.update_from_set(solns.pop())

    return solution


def eliminate_contained(board, solution=None):
    solution = solution or Solution(board)

    def falsify(cells):
        for i, j in cells:
            if solution[i][j] is None:
                solution[i][j] = False

    # areas containing entire columns or rows

    row_areas = {}
    col_areas = {}
    for i, j in board.cell_index_iter:
        area = board.area_for_cell(i, j)
        row_areas.setdefault(i, set()).add(area)
        col_areas.setdefault(j, set()).add(area)

    for r, areas in row_areas.items():
        if len(areas) == 1:
            # row is entirely contained in area, byyeee other cells
            falsify((i, j) for i, j in areas.pop() if i != r)

    for c, areas in col_areas.items():
        if len(areas) == 1:
            # row is entirely contained in area, byyeee other cells
            falsify((i, j) for i, j in areas.pop() if j != c)

    # (unsolved cells of) areas fully contained by row or col

    for area in board.areas:
        unsolved_cells = solution.unknown_cells(area=area)
        if len(unsolved_cells) == 0:
            continue

        rows, cols = map(set, zip(*unsolved_cells))
        if len(rows) == 1:
            # all cells in one row
            r = rows.pop()
            falsify((r, c) for c in range(board.size) if (r, c) not in area)

        if len(cols) == 1:
            # all cells in one col
            c = cols.pop()
            falsify((r, c) for r in range(board.size) if (r, c) not in area)

    return solution


def brute_force(board, solution=None):
    solution = solution or Solution(board)

    unsolved_areas = [area for area in board.areas if solution.count_unknown(area=area)]
    # solve smallest first to apply most constraints
    unsolved_areas = sorted(unsolved_areas, key=lambda a: solution.count_unknown(area=a))

    if len(unsolved_areas) == 0 and solution.verify():
        return solution

    for a in unsolved_areas:
        next_solns = []
        for a_soln in solve_area(board, a, solution):
            tmp_soln = solution.copy()
            tmp_soln.update_from_set(a_soln)
            next_solns.append(tmp_soln)

        for tmp_soln in sorted(next_solns, key=lambda s: s.count_unknown()):
            # recurse with area solution applied
            res = brute_force(board, tmp_soln)

            if res:
                return res

    return None


def solve(board):
    """ Top level solve procedure for a board """

    past_solution = set()
    solution = None

    while True:
        # look for forced false cells
        solution = eliminate_contained(board, solution)

        # solve the fully defined areas
        solution = solve_fully_defined_areas(board, solution)

        new_soln = solution.to_set()
        if past_solution == new_soln:
            break

        past_solution = new_soln

    # board.draw_solution_with_ruled_out(solution)
    # print("Undefined:", sum(solution[i][j] is None for i,j in board.cell_index_iter))
    # BRUTE!
    return brute_force(board, solution)
