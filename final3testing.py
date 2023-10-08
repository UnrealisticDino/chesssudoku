import pygame
import random
import logging

logging.basicConfig(
    level=logging.INFO,
    filename='app_logs.log',  # Specify the filename for the log file
    filemode='w',  # 'w' for write mode, creates a new file each time
    format='%(asctime)s - %(levelname)s - %(message)s'
)
# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 540, 540
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku Maker")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)

# Fonts
FONT_SMALL = pygame.font.SysFont(None, 30)
FONT_LARGE = pygame.font.SysFont(None, 60)

# Game clock
clock = pygame.time.Clock()

# Create log file
log_file = "sudoku_logs.txt"
open(log_file, "a").close()  # Create the log file if it doesn't exist

def find_most_constrained_cell(puzzle):
    min_possible = 10  # More than the maximum possible
    min_cells = []
    for row in range(9):
        for col in range(9):
            if puzzle[row][col] == 0:
                possible_numbers = get_numbers(puzzle, row, col)  # Use get_numbers instead of get_possible_numbers
                if len(possible_numbers) < min_possible:
                    min_possible = len(possible_numbers)
                    min_cells = [(row, col)]
                elif len(possible_numbers) == min_possible:
                    min_cells.append((row, col))
    return random.choice(min_cells) if min_cells else (-1, -1)

def get_possible_numbers(puzzle, row, col):
    row_nums = set(puzzle[row])
    col_nums = set(puzzle[i][col] for i in range(9))

    box_start_row, box_start_col = row - row % 3, col - col % 3
    box_nums = set(puzzle[i][j] for i in range(box_start_row, box_start_row + 3) for j in range(box_start_col, box_start_col + 3))

    used_nums = row_nums | col_nums | box_nums
    possible_nums = set(range(1, 10)) - used_nums

    return possible_nums

def generate_sudoku():
    puzzle = [[0] * 9 for _ in range(9)]
    solve_sudoku(puzzle)
    if not is_valid_sudoku(puzzle):
        with open(log_file, "a") as f:
            f.write(str(puzzle) + "\n")
    return puzzle

def solve_sudoku(puzzle):
    row, col = find_most_constrained_cell(puzzle)
    if row == -1 and col == -1:
        return True

    possible_numbers = list(get_possible_numbers(puzzle, row, col))
    random.shuffle(possible_numbers)  # Shuffle the numbers for random placement
     
    for num in possible_numbers:
        if not is_valid_placement(puzzle, row, col, num):
            continue

        puzzle[row][col] = num
        
        # Check if the display is still open and draw the puzzle
        if pygame.display.get_init():
            pygame.event.pump()
            draw_puzzle(puzzle)
        
        # Forward checking: If any neighboring cell has no possible numbers left, backtrack immediately
        valid_forward_check = True
        for r, c in get_neighboring_cells(puzzle, row, col):
            possible_nums_for_neighbor = get_possible_numbers(puzzle, r, c)
            if len(possible_nums_for_neighbor) == 0:
                valid_forward_check = False
                break

        if not valid_forward_check:
            puzzle[row][col] = 0
            continue

        if solve_sudoku(puzzle):
            return True
        puzzle[row][col] = 0
    return False

def get_possible_numbers_after_placement(puzzle, row, col, num):
    temp_puzzle = [r.copy() for r in puzzle]
    temp_puzzle[row][col] = num
    return get_possible_numbers(temp_puzzle, row, col)

def get_neighboring_cells(puzzle, row, col):
    neighbors = []
    for i in range(9):
        if i != row and puzzle[i][col] == 0:
            neighbors.append((i, col))
        if i != col and puzzle[row][i] == 0:
            neighbors.append((row, i))
    box_start_row, box_start_col = row - row % 3, col - col % 3
    for i in range(box_start_row, box_start_row + 3):
        for j in range(box_start_col, box_start_col + 3):
            if (i != row or j != col) and puzzle[i][j] == 0:
                neighbors.append((i, j))
    return neighbors

def get_numbers(puzzle, row, col):
    possible_numbers = get_possible_numbers(puzzle, row, col)
    
    valid_numbers = []
    for num in possible_numbers:
        if is_valid_for_king_knight_adjacent(puzzle, row, col, num):
            valid_numbers.append(num)
            
    return valid_numbers

def is_valid_for_king_knight_adjacent(puzzle, row, col, num):
    # Check knight moves
    knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
    for move in knight_moves:
        r = row + move[0]
        c = col + move[1]
        if is_valid_cell(r, c) and puzzle[r][c] == num:
            return False
    
    # Check king moves
    king_moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    for move in king_moves:
        r = row + move[0]
        c = col + move[1]
        if is_valid_cell(r, c) and puzzle[r][c] == num:
            return False

    # Check adjacent cells
    adjacent_moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for move in adjacent_moves:
        r = row + move[0]
        c = col + move[1]
        if is_valid_cell(r, c):
            adjacent_num = puzzle[r][c]
            if adjacent_num != 0 and abs(num - adjacent_num) == 1:
                return False

    return True

def is_valid_placement(puzzle, row, col, num):
    return is_valid_for_king_knight_adjacent(puzzle, row, col, num)

def is_valid_cell(row, col):
    return 0 <= row < 9 and 0 <= col < 9

def find_empty_cell(puzzle):
    empty_cells = [(row, col) for row in range(9) for col in range(9) if puzzle[row][col] == 0]
    if not empty_cells:
        return -1, -1
    return random.choice(empty_cells)

def is_valid_sudoku(puzzle):
    for row in range(9):
        if not is_valid_row(puzzle[row]):
            return False

    for col in range(9):
        column = [puzzle[row][col] for row in range(9)]
        if not is_valid_row(column):
            return False

    for start_row in range(0, 9, 3):
        for start_col in range(0, 9, 3):
            square = [
                puzzle[row][col]
                for row in range(start_row, start_row + 3)
                for col in range(start_col, start_col + 3)
            ]
            if not is_valid_row(square):
                return False

    return True

def is_valid_row(row):
    numbers = [n for n in row if n != 0]
    return len(set(numbers)) == len(numbers)

def draw_puzzle(puzzle):
    WINDOW.fill(WHITE)
    for i in range(9):
        for j in range(9):
            cell_value = puzzle[i][j]
            if cell_value != 0:
                text = FONT_LARGE.render(str(cell_value), True, BLACK)
                text_rect = text.get_rect(center=(j * 60 + 30, i * 60 + 30))
                WINDOW.blit(text, text_rect)
    for i in range(10):
        if i % 3 == 0:
            pygame.draw.line(WINDOW, BLACK, (0, i * 60), (540, i * 60), 3)
            pygame.draw.line(WINDOW, BLACK, (i * 60, 0), (i * 60, 540), 3)
        else:
            pygame.draw.line(WINDOW, GRAY, (0, i * 60), (540, i * 60), 1)
            pygame.draw.line(WINDOW, GRAY, (i * 60, 0), (i * 60, 540), 1)
    pygame.display.update()

def save_puzzle_to_file(puzzle):
    with open("sudoku_logs.txt", "a") as file:
        file.write(str(puzzle) + "\n\n")

def main():
    while True:
        # Generate and validate a random Sudoku puzzle
        puzzle = generate_sudoku()
        while not is_valid_sudoku(puzzle):
            puzzle = generate_sudoku()

        # Save the valid puzzle to the file
        save_puzzle_to_file(puzzle)

        # Main game loop
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            draw_puzzle(puzzle)
            clock.tick(60)

        pygame.quit()

if __name__ == '__main__':
    main()