from star_battle import Board, get_local_puzzle

board = Board.from_krazydad(get_local_puzzle())
hlight = board.cells_within_bounds(0, 0)
areas = board.areas

for a in areas:
    board.draw(highlight=a)
    input("mmmm")
