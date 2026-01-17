import curses
import random
import time
from dataclasses import dataclass
from typing import List, Tuple

BOARD_WIDTH = 10
BOARD_HEIGHT = 20
TICK_RATE = 0.5

SHAPES = {
    "I": [[1, 1, 1, 1]],
    "O": [[1, 1], [1, 1]],
    "T": [[0, 1, 0], [1, 1, 1]],
    "S": [[0, 1, 1], [1, 1, 0]],
    "Z": [[1, 1, 0], [0, 1, 1]],
    "J": [[1, 0, 0], [1, 1, 1]],
    "L": [[0, 0, 1], [1, 1, 1]],
}

@dataclass
class Piece:
    shape: List[List[int]]
    x: int
    y: int

    def rotate(self) -> List[List[int]]:
        return [list(row) for row in zip(*self.shape[::-1])]


def create_board() -> List[List[int]]:
    return [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]


def valid_position(board: List[List[int]], shape: List[List[int]], x: int, y: int) -> bool:
    for row_idx, row in enumerate(shape):
        for col_idx, cell in enumerate(row):
            if not cell:
                continue
            board_x = x + col_idx
            board_y = y + row_idx
            if board_x < 0 or board_x >= BOARD_WIDTH or board_y >= BOARD_HEIGHT:
                return False
            if board_y >= 0 and board[board_y][board_x]:
                return False
    return True


def merge_piece(board: List[List[int]], piece: Piece) -> None:
    for row_idx, row in enumerate(piece.shape):
        for col_idx, cell in enumerate(row):
            if cell:
                board_y = piece.y + row_idx
                board_x = piece.x + col_idx
                if 0 <= board_y < BOARD_HEIGHT and 0 <= board_x < BOARD_WIDTH:
                    board[board_y][board_x] = 1


def clear_lines(board: List[List[int]]) -> int:
    new_board = [row for row in board if any(cell == 0 for cell in row)]
    cleared = BOARD_HEIGHT - len(new_board)
    for _ in range(cleared):
        new_board.insert(0, [0 for _ in range(BOARD_WIDTH)])
    board[:] = new_board
    return cleared


def draw_board(stdscr: curses.window, board: List[List[int]], piece: Piece, score: int) -> None:
    stdscr.clear()
    stdscr.addstr(0, 0, "Tetris (q to quit)")
    stdscr.addstr(1, 0, f"Score: {score}")

    display = [row[:] for row in board]
    for row_idx, row in enumerate(piece.shape):
        for col_idx, cell in enumerate(row):
            if cell:
                board_y = piece.y + row_idx
                board_x = piece.x + col_idx
                if 0 <= board_y < BOARD_HEIGHT and 0 <= board_x < BOARD_WIDTH:
                    display[board_y][board_x] = 1

    for y, row in enumerate(display):
        line = "|" + "".join("[]" if cell else "  " for cell in row) + "|"
        stdscr.addstr(y + 3, 0, line)
    stdscr.addstr(BOARD_HEIGHT + 3, 0, "+" + "--" * BOARD_WIDTH + "+")
    stdscr.refresh()


def new_piece() -> Piece:
    shape = random.choice(list(SHAPES.values()))
    x = (BOARD_WIDTH - len(shape[0])) // 2
    return Piece(shape=shape, x=x, y=-1)


def run_game(stdscr: curses.window) -> None:
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(50)

    board = create_board()
    piece = new_piece()
    score = 0
    last_tick = time.time()

    while True:
        now = time.time()
        if now - last_tick >= TICK_RATE:
            last_tick = now
            if valid_position(board, piece.shape, piece.x, piece.y + 1):
                piece.y += 1
            else:
                merge_piece(board, piece)
                score += clear_lines(board) * 100
                piece = new_piece()
                if not valid_position(board, piece.shape, piece.x, piece.y):
                    draw_board(stdscr, board, piece, score)
                    stdscr.addstr(BOARD_HEIGHT + 5, 0, "Game Over! Press any key to exit.")
                    stdscr.nodelay(False)
                    stdscr.getch()
                    break

        key = stdscr.getch()
        if key == ord("q"):
            break
        if key in (curses.KEY_LEFT, ord("a")):
            if valid_position(board, piece.shape, piece.x - 1, piece.y):
                piece.x -= 1
        elif key in (curses.KEY_RIGHT, ord("d")):
            if valid_position(board, piece.shape, piece.x + 1, piece.y):
                piece.x += 1
        elif key in (curses.KEY_DOWN, ord("s")):
            if valid_position(board, piece.shape, piece.x, piece.y + 1):
                piece.y += 1
        elif key in (curses.KEY_UP, ord("w"), ord(" ")):
            rotated = piece.rotate()
            if valid_position(board, rotated, piece.x, piece.y):
                piece.shape = rotated

        draw_board(stdscr, board, piece, score)


def main() -> None:
    curses.wrapper(run_game)


if __name__ == "__main__":
    main()
