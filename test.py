import time

from star_battle import Board, get_local_puzzle, solve, verify_solution

board = Board.from_krazydad(get_local_puzzle())

start = time.time()
solution = solve(board)
end = time.time()
print("Got solution?", solution is not None, f"in {end - start:.2f}")

board.draw(
    highlight={
        (i, j) for i, row in enumerate(solution) for j, cell in enumerate(row) if cell
    }
)
