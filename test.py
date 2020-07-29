import time

from star_battle import *

try:
    # board = Board.get_krazy_dad(kind=10, volume=1, book=9, puzzle=5) # can do
    # board = Board.get_krazy_dad(kind=10, volume=1, book=11, puzzle=12)
    # print("Got board, solving...", board.stars)
    board = Board.from_krazydad(get_local_puzzle(num=1))
    # board.draw()

    start = time.time()
    solution = solve(board)
    end = time.time()
    print("Got solution?", solution is not None, f"in {end - start:.2f}")

    if solution:
        board.check_solution(solution)
        board.draw_solution(solution)
except KeyboardInterrupt:
    print()
    board.draw(with_solution=True)
