import time

from star_battle import *

board = Board.from_krazydad(get_local_puzzle())

start = time.time()
solution = solve(board)
end = time.time()
print("Got solution?", solution is not None, f"in {end - start:.2f}")

if solution:
    board.draw_solution(solution)
