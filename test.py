import time

from star_battle import *

# board = Board.get_krazy_dad(kind=10, volume=1, book=9, puzzle=5)
# print("Got board, solving...")
board = Board.from_krazydad(get_local_puzzle(num=1))

start = time.time()
solution = solve(board)
end = time.time()
print("Got solution?", solution is not None, f"in {end - start:.2f}")

if solution:
    board.check_solution(solution)
    board.draw_solution(solution)
