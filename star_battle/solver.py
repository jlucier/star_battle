import copy
from functools import reduce
import itertools
import time

from .board import bcolors


# Solution data helpers


def empty_solution(board, value=None):
    return [[value] * board.size for _ in range(board.size)]


def solution_to_set(solution):
    return frozenset((i, j) for i, row in enumerate(solution) for j, cell in enumerate(row) if cell)


def solution_from_set(solution_set, board, value=False):
    solution = empty_solution(board, value=value)
    for i, j in solution_set:
        solution[i][j] = True

    return solution


def update_solution_from_set(board, solution, new_set):
    for i, j in new_set:
        solution[i][j] = True

    for i, j in board.cell_index_iter:
        if not can_place_star(board, i, j, solution):
            solution[i][j] = False


# Solve helpers


def can_place_star(board, row, col, solution):
    """ Check if row,col can contain a star based board / running solution """

    # check neighbors (no start can neighbor another)
    for i, j in itertools.product(range(-1, 2), range(-1, 2)):
        r = row + i
        c = col + j

        if (i == 0 and j == 0) or not board.is_valid_cell(r, c):
            continue

        if solution[r][c]:
            return False

    # check counts for areas, rows, cols

    # determine if we need to add one based on whether the currect cell has a star already
    add = 0 if solution[row][col] else 1

    sol_sum = lambda it: sum(map(bool, it))

    return all(
        count + add <= board.stars
        for count in (
            sol_sum(solution[row]),  # stars in the row
            sol_sum(solution[i][col] for i in range(board.size)),  # stars in the column
            sol_sum(solution[i][j] for i, j in board.area_for_cell(row, col)),  # stars in the area
        )
    )


def solve_area(board, area, solution=None):
    """ Get solutions for a certain area given a working solution """

    solution = solution or empty_solution(board)
    ret = set()

    for i, j in area:
        if solution[i][j] is None:
            options = [False]
            if can_place_star(board, i, j, solution):
                options.append(True)

            for v in options:
                solution[i][j] = v
                ret.update(solve_area(board, area, solution))
                solution[i][j] = None

    if (
        all(solution[i][j] is not None for i, j in area)
        and sum(solution[i][j] for i, j in area) == board.stars
    ):
        ret.add(solution_to_set(solution))

    return ret


def solve_fully_defined_areas(board, solution=None):
    solution = solution or empty_solution(board)

    ordered_areas = list(sorted(board.areas, key=len))

    already_revisited = set()
    # find all fully defined areas and merge the solutions
    while len(ordered_areas):
        area = ordered_areas.pop(0)

        # skip areas with too many cells undefined
        if sum(solution[i][j] is None for i, j in area) > 6:
            continue

        solns = solve_area(board, area, solution)

        if len(solns) > 1:
            if area not in already_revisited:
                ordered_areas.append(area)
                already_revisited.add(area)

            # TODO look for cells that are eliminated by all possible solutions
            s = solns.pop()
            common_cells = reduce(lambda a, b: a.intersection(b), solns, s)
            if len(common_cells):
                update_solution_from_set(board, solution, common_cells)

        else:
            # something we revisted became determined, reset revisit history
            if area in already_revisited:
                already_revisited.clear()

            update_solution_from_set(board, solution, solns.pop())

    return solution


def eliminate_contained(board, solution=None):
    solution = solution or empty_solution(board)

    def falsify(cells):
        cells = list(cells)
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
        unsolved_cells = list((i, j) for i, j in area if solution[i][j] is None)
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
    solution = solution or [[None] * board.size for _ in range(board.size)]

    unsolved_areas = [area for area in board.areas if any(solution[r][c] is None for r, c in area)]

    if len(unsolved_areas) == 0 and verify_solution(board, solution):
        return solution

    for a in unsolved_areas:
        for a_soln in solve_area(board, a, solution):
            tmp_soln = copy.deepcopy(solution)
            update_solution_from_set(board, tmp_soln, a_soln)

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

        new_soln = solution_to_set(solution)
        if past_solution == new_soln:
            break

        past_solution = new_soln

    # BRUTE!
    return brute_force(board, solution)


def verify_solution(board, solution):
    # check number of stars
    if not sum(sum(row) for row in solution) == board.stars * board.size:
        return False

    for i, row in enumerate(solution):
        for j, cell in enumerate(row):
            if cell and not can_place_star(board, i, j, solution):
                return False

    return True
