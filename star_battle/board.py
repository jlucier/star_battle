from dataclasses import dataclass
from math import ceil
from pprint import pprint


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def red(s):
    return bcolors.FAIL + s + bcolors.ENDC


@dataclass(frozen=True)
class Cell:
    lb: bool = False
    rb: bool = False
    tb: bool = False
    bb: bool = False

    def __str__(self):
        return sum(
            (
                "l" if self.lb else "",
                "r" if self.rb else "",
                "t" if self.tb else "",
                "b" if self.bb else "",
            )
        )


@dataclass(frozen=True)
class Board:
    cells: [[Cell]]
    stars: int
    size: int
    solution: str

    @staticmethod
    def from_krazydad(puzzle_data):
        size = puzzle_data["height"]

        cells = [[None] * size for _ in range(size)]
        puzz_string = puzzle_data["puzz"]
        for i, c in enumerate(puzz_string):
            lb = rb = tb = bb = False

            if i % size != size - 1:
                # we aren't at the end of a row
                if c != puzz_string[i + 1]:
                    rb = True

            if i + size < len(puzz_string) and c != puzz_string[i + size]:
                bb = True

            row = i // size
            col = i % size

            if row > 0:
                # top border if cell above has bottom border
                tb = cells[row - 1][col].bb
            if col > 0:
                # left border if cell to left has right border
                lb = cells[row][col - 1].rb

            cells[row][col] = Cell(lb=lb, rb=rb, tb=tb, bb=bb)

        return Board(
            cells=cells,
            size=size,
            stars=puzzle_data["stars"],
            solution=puzzle_data["solved"],
        )

    def draw(self, cell_size=9, with_solution=False):
        horiz_border = "\u2504"
        vert_border = "\u250A"

        full_len = (cell_size - 1) * self.size
        white_space = cell_size // 2 - 1

        def draw_line(start, end, corner="", conn="\u2500"):
            mid_section = (conn * (cell_size - 2) + corner) * self.size
            return list(f"{start}{mid_section[:-1]}{end}")

        board = [draw_line("\u250C", "\u2510", "\u252C")]
        for i in range(self.size):
            for _ in range(white_space):
                board.append(draw_line("\u2502", "\u2502", corner="\u2502", conn=" "))
            if i != self.size - 1:
                board.append(draw_line("\u251C", "\u2524", "\u253C"))

        board.append(draw_line("\u2514", "\u2518", corner="\u2534", conn="\u2500"))

        for i, row in enumerate(self.cells):
            for j, cell in enumerate(row):
                r = white_space + i * (cell_size // 2) - 1
                c = white_space + j * (cell_size - 1) + 1

                if cell.bb:
                    for x in range(-white_space // 2 - 1, ceil(white_space / 2) + 2):
                        board[r + (white_space - 1)][c + x] = red("\u2501")

                    if j == 0:
                        board[r + (white_space - 1)][0] = red("\u251D")
                    elif j == self.size - 1:
                        board[r + (white_space - 1)][-1] = red("\u2525")

                if cell.rb:
                    for x in range(-white_space // 4, ceil(white_space / 4) + 1):
                        board[r + x][c + white_space + 1] = red("\u2503")

                    if i == 0:
                        board[0][c + white_space + 1] = red("\u2530")
                    elif i == self.size - 1:
                        board[-1][c + white_space + 1] = red("\u2538")

                if (cell.rb or cell.bb) and i + 1 < self.size and j + 1 < self.size:
                    board[r + (white_space - 1)][c + white_space + 1] = red("\u254B")

                if with_solution and self.solution[i * self.size + j] == "1":
                    board[r][c] = "*"

        for row in board:
            print("".join(row))
