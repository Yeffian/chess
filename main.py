import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (118, 150, 86)
BEIGE = (238, 238, 210)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess")

PIECES = {}
for piece in ["bp", "wp", "br", "wr", "bn", "wn", "bb", "wb", "bq", "wq", "bk", "wk"]:
    PIECES[piece] = pygame.transform.scale(
        pygame.image.load(f"assets/{piece}.png"), (SQUARE_SIZE, SQUARE_SIZE)
    )

board = [
    ["br", "bn", "bb", "bq", "bk", "bb", "bn", "br"],
    ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
    ["wr", "wn", "wb", "wq", "wk", "wb", "wn", "wr"],
]

def draw_board(valid_moves=None):
    for row in range(ROWS):
        for col in range(COLS):
            color = BEIGE if (row + col) % 2 == 0 else BROWN
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            if valid_moves and (row, col) in valid_moves:
                pygame.draw.rect(screen, (0, 255, 0), (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 5)

def draw_pieces():
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece != "":
                screen.blit(PIECES[piece], (col * SQUARE_SIZE, row * SQUARE_SIZE))

def get_position_from_mouse(pos):
    x, y = pos
    return y // SQUARE_SIZE, x // SQUARE_SIZE

def is_valid_move(piece, start_row, start_col, end_row, end_col):
    if piece == "":
        return False

    color = "w" if piece[0] == "w" else "b"
    target_piece = board[end_row][end_col]

    if target_piece != "" and target_piece[0] == color:
        return False

    delta_row, delta_col = abs(end_row - start_row), abs(end_col - start_col)

    if piece[1] == "p":
        direction = -1 if color == "w" else 1
        if start_col == end_col and target_piece == "":
            if (delta_row == 1 and direction * (end_row - start_row) > 0) or \
               (delta_row == 2 and start_row in (1, 6) and board[start_row + direction][start_col] == "" and direction * (end_row - start_row) > 0):
                return True
        elif delta_row == 1 and delta_col == 1 and target_piece != "" and target_piece[0] != color:
            return True
    elif piece[1] == "r":
        if delta_row == 0 or delta_col == 0:
            return path_is_clear(start_row, start_col, end_row, end_col)
    elif piece[1] == "n":
        if (delta_row, delta_col) in [(2, 1), (1, 2)]:
            return True
    elif piece[1] == "b":
        if delta_row == delta_col:
            return path_is_clear(start_row, start_col, end_row, end_col)
    elif piece[1] == "q":
        if delta_row == delta_col or delta_row == 0 or delta_col == 0:
            return path_is_clear(start_row, start_col, end_row, end_col)
    elif piece[1] == "k":
        if max(delta_row, delta_col) == 1:
            return True

    return False

def path_is_clear(start_row, start_col, end_row, end_col):
    step_row = (end_row - start_row) // max(abs(end_row - start_row), 1) if end_row != start_row else 0
    step_col = (end_col - start_col) // max(abs(end_col - start_col), 1) if end_col != start_col else 0

    current_row, current_col = start_row + step_row, start_col + step_col
    while (current_row, current_col) != (end_row, end_col):
        if board[current_row][current_col] != "":
            return False
        current_row += step_row
        current_col += step_col

    return True

def get_valid_moves(piece, start_row, start_col):
    valid_moves = []
    for end_row in range(ROWS):
        for end_col in range(COLS):
            if is_valid_move(piece, start_row, start_col, end_row, end_col):
                temp_piece = board[end_row][end_col]
                board[end_row][end_col] = board[start_row][start_col]
                board[start_row][start_col] = ""

                if not is_in_check(piece[0]):
                    valid_moves.append((end_row, end_col))

                board[start_row][start_col] = board[end_row][end_col]
                board[end_row][end_col] = temp_piece
    return valid_moves

def is_in_check(color):
    king_position = None
    for row in range(ROWS):
        for col in range(COLS):
            if board[row][col] == f"{color}k":
                king_position = (row, col)
                break

    if not king_position:
        return False

    king_row, king_col = king_position
    opponent_color = "b" if color == "w" else "w"

    for row in range(ROWS):
        for col in range(COLS):
            if board[row][col] != "" and board[row][col][0] == opponent_color:
                if is_valid_move(board[row][col], row, col, king_row, king_col):
                    return True

    return False

# Main loop
selected_piece = None
valid_moves = []
running = True
current_turn = "w"
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            row, col = get_position_from_mouse(pygame.mouse.get_pos())
            if selected_piece:
                if (row, col) in valid_moves:
                    board[row][col] = selected_piece
                    board[selected_row][selected_col] = ""
                    if is_in_check(current_turn):
                        board[selected_row][selected_col] = selected_piece
                        board[row][col] = ""
                    else:
                        current_turn = "b" if current_turn == "w" else "w"
                selected_piece = None
                valid_moves = []
            else:
                if board[row][col] != "" and board[row][col][0] == current_turn:
                    selected_piece = board[row][col]
                    selected_row, selected_col = row, col
                    valid_moves = get_valid_moves(selected_piece, selected_row, selected_col)

    draw_board(valid_moves)
    draw_pieces()
    pygame.display.flip()

pygame.quit()
sys.exit()
