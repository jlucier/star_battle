import itertools


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
            sol_sum(
                solution[i][j] for i, j in board.area_for_cell(row, col)
            ),  # stars in the area
        )
    )


def solve(board, solution=None):
    solution = solution or [[None] * board.size for _ in range(board.size)]

    for i, j in itertools.product(range(board.size), range(board.size)):
        if solution[i][j] is None:
            solution[i][j] = can_place_star(board, i, j, solution)
            result = solve(board, solution)

            # if we got a solution, exit
            if result:
                return result

            solution[i][j] = None

    if all(c is not None for row in solution for c in row) and verify_solution(
        board, solution
    ):
        return solution

    return None


def verify_solution(board, solution):
    # check number of stars
    if not sum(sum(row) for row in solution) == board.stars * board.size:
        return False

    for i, row in enumerate(solution):
        for j, cell in enumerate(row):
            if cell and not can_place_star(board, i, j, solution):
                return False

    return True
