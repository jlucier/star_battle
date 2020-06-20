from dataclasses import dataclass
from math import ceil
from pprint import pprint


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

            if i % size != 1 and i + 1 < len(
                puzz_string
            ):  # we aren't at the end of a row
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
                lb = cells[row][col - 1].lb

            cells[row][col] = Cell(lb=lb, rb=rb, tb=tb, bb=bb)

        return Board(
            cells=cells,
            size=size,
            stars=puzzle_data["stars"],
            solution=puzzle_data["solved"],
        )

    def draw(self, cell_size=9):
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
                board[r][c] = "*"

                if cell.tb:
                    for x in range(-white_space // 2, ceil(white_space / 2) + 1):
                        board[r - (white_space - 1)][c + x] = "\u2550"

        for row in board:
            print("".join(row))
