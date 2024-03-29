from dataclasses import dataclass
from functools import partial
import itertools
from math import ceil

from .board_fetcher import download_puzzle


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def colored(s, color):
    return color + s + bcolors.ENDC


red = partial(colored, color=bcolors.FAIL)


@dataclass(frozen=True)
class Cell:
    lb: bool = False
    rb: bool = False
    tb: bool = False
    bb: bool = False


@dataclass
class Board:
    cells: list[list[Cell]]
    stars: int
    size: int
    solution: list[list[bool]]

    def __post_init__(self):
        self._areas = self._get_areas()
        self._area_lookup = {tup: a for a in self.areas for tup in a}

    @classmethod
    def get_krazy_dad(cls, *args, **kwargs):
        return cls.from_krazydad(download_puzzle(*args, **kwargs))

    @classmethod
    def from_krazydad(cls, puzzle_data):
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

        # reformat solution
        solution = [[False] * size for _ in range(size)]
        for i, c in enumerate(puzzle_data["solved"]):
            row = i // size
            col = i % size
            solution[row][col] = c == "1"

        return cls(
            cells=cells,
            size=size,
            stars=puzzle_data["stars"],
            solution=solution,
        )

    @property
    def cell_index_iter(self):
        return itertools.product(range(self.size), range(self.size))

    def is_valid_cell(self, i=0, j=0):
        return 0 <= i < self.size and 0 <= j < self.size

    def draw_solution(self, solution):
        self.draw(
            highlight={
                (i, j): bcolors.OKGREEN
                for i, row in enumerate(solution)
                for j, cell in enumerate(row)
                if cell
            }
        )

    def draw_solution_with_ruled_out(self, solution, highlight=None):
        highlight = dict(highlight or {})
        highlight.update(
            {
                (i, j): bcolors.FAIL if solution[i][j] is False else bcolors.OKGREEN
                for i, j in self.cell_index_iter
                if solution[i][j] is not None
            }
        )
        self.draw(highlight=highlight)

    def draw(
        self,
        cell_size=9,
        with_solution=False,
        highlight: dict | None = None,
        highlight_c=bcolors.OKGREEN,
    ):
        highlight = highlight or dict()
        white_space = cell_size // 2 - 1

        def draw_line(start, end, corner="", conn="\u2500"):
            mid_section = (conn * (cell_size - 2) + corner) * self.size
            return list(f"{start}{mid_section[:-1]}{end}")

        # starting layout

        board = [draw_line("\u250C", "\u2510", "\u252C")]
        for i in range(self.size):
            for _ in range(white_space):
                board.append(draw_line("\u2502", "\u2502", corner="\u2502", conn=" "))

            if i != self.size - 1:
                board.append(draw_line("\u251C", "\u2524", "\u253C"))

        board.append(draw_line("\u2514", "\u2518", corner="\u2534", conn="\u2500"))

        # color borders

        for i, row in enumerate(self.cells):
            for j, cell in enumerate(row):
                r = white_space + i * (cell_size // 2) - 1
                c = white_space + j * (cell_size - 1) + 1

                # make red edges

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

                # make red top left or bottom right chars

                if (cell.rb or cell.bb) and self.is_valid_cell(i + 1, j + 1):
                    board[r + (white_space - 1)][c + white_space + 1] = red("\u254B")

                if (cell.lb or cell.tb) and self.is_valid_cell(i - 1, j - 1):
                    board[r - (white_space - 1)][c - (white_space + 1)] = red("\u254B")

                # add stars

                if with_solution and self.solution[i][j]:
                    board[r][c] = "*"

                if (i, j) in highlight:
                    color = highlight[(i, j)] if isinstance(highlight, dict) else highlight_c
                    board[r][c] = colored("*", color)

        for i, row in enumerate(board):
            # inverse equation from above
            grid_row = (i - white_space + 1) / (cell_size // 2)
            grid_row = int(grid_row) if int(grid_row) == grid_row else None
            print("".join(row) + (f" {grid_row}" if grid_row is not None else ""))

        final_row = ""
        for j in range(len(board[0])):
            # inverse equation from above
            grid_col = (j - white_space - 1) / (cell_size - 1)
            grid_col = int(grid_col) if int(grid_col) == grid_col else None

            if grid_col is not None:
                str_label = str(grid_col)
                if len(str_label) > 1:
                    final_row = final_row[:-1] + str_label
                else:
                    final_row += str_label
            else:
                final_row += " "

        print(final_row)

    def cells_within_bounds(self, row: int, col: int, cells: set | None = None):
        c = self.cells[row][col]
        cells = {(row, col)} if not cells else cells.union({(row, col)})

        # recurse only to cardinal directions
        for x, y in [(-1, 0), (0, -1), (0, 1), (1, 0)]:
            new_r = row + x
            new_c = col + y

            # skip invalid or already visited
            if not self.is_valid_cell(new_r, new_c) or (new_r, new_c) in cells:
                continue

            # skip if there's a border between
            if (x == -1 and c.tb) or (x == 1 and c.bb) or (y == -1 and c.lb) or (y == 1 and c.rb):
                continue

            cells.update(self.cells_within_bounds(new_r, new_c, cells))

        return cells

    def _get_areas(self):
        areas = []
        accounted_for_cells = set()

        for i, j in self.cell_index_iter:
            # skip cells already in known areas
            if (i, j) in accounted_for_cells:
                continue

            # find area cell i,j belongs to
            a = self.cells_within_bounds(i, j)
            # account for all cells in said area
            accounted_for_cells.update(a)
            # save
            areas.append(frozenset(a))

        return areas

    @property
    def areas(self):
        return self._areas

    def area_for_cell(self, row, col):
        return self._area_lookup[(row, col)]

    def check_solution(self, candidate):
        for i, j in self.cell_index_iter:
            assert candidate[i][j] == self.solution[i][j], "Incorrect solution"
