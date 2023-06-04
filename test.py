import time

from star_battle import *

try:
    # EZ
    # board = Board.get_krazy_dad(kind=10, volume=1, book=9, puzzle=5)
    # board = Board.get_krazy_dad(kind=10, volume=1, book=11, puzzle=12)
    # board = Board.get_krazy_dad(kind=10, volume=4, book=90, puzzle=18)  # ~36s
    # board = Board.get_krazy_dad(kind=14, volume=1, book=52, puzzle=22)  # ~96s, parllel 0.45s
    # board = Board.get_krazy_dad(kind=8, volume=1, book=94, puzzle=2)  # ~17s
    # board = Board.get_krazy_dad(kind=8, volume=2, book=74, puzzle=20)  # ~11s
    # board = Board.get_krazy_dad(kind=8, volume=4, book=94, puzzle=21)  # now fast
    # board = Board.get_krazy_dad(kind=8, volume=4, book=85, puzzle=7)  # now fast
    # board = Board.get_krazy_dad(kind=8, volume=3, book=87, puzzle=4)  # 2.8s
    # board = Board.get_krazy_dad(kind=10, volume=3, book=95, puzzle=13)  # 3.1s

    board = Board.get_krazy_dad(kind=14, volume=4, book=44, puzzle=7)  # fucked

    # board = Board.from_krazydad(get_local_puzzle(num=1))
    # board = Board.from_krazydad(get_random_puzzle())
    # board.draw()
    print("Got board, solving...", board.stars)
    start = time.time()
    solution = solve(board)
    end = time.time()
    print("Got solution?", solution is not None, f"in {end - start:.2f}")

    if solution:
        board.draw_solution(solution)
        board.check_solution(solution)
except KeyboardInterrupt:
    print()
    board.draw(with_solution=True)
