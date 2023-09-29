from collections import defaultdict
import sys
import csv
import time
from copy import deepcopy

n = len(sys.argv)
filename = ""
mode = ""
board = []
printedBoard = []
nodes = 0

def load_board():
    # Open the CSV file for reading
    with open(filename, newline='') as csvfile:
        # Create a CSV reader object
        csvreader = csv.reader(csvfile, delimiter=',')
        # Loop through each row in the CSV file
        for row in csvreader:
            # Append the row to the data list as a list
            printedBoard.append(row)
            board_row = [int(cell) if cell != 'X' else 0 for cell in row]
            board.append(board_row)
    
    
    start_mode()


def is_valid_board(board): #checks if the current board is valid by checking each row, column, and box
    def is_valid_row(board):
        for row in board:
            if not is_valid_group(row):
                return False
        return True

    def is_valid_col(board):
        for col in range(9):
            if not is_valid_group([board[row][col] for row in range(9)]):
                return False
        return True

    def is_valid_box(board):
        for row in range(0, 9, 3):
            for col in range(0, 9, 3):
                box = [board[row+i][col+j] for i in range(3) for j in range(3)]
                if not is_valid_group(box):
                    return False
        return True

    def is_valid_group(group):
        nums = set(range(1, 10))
        return set(group) == nums

    return is_valid_row(board) and is_valid_col(board) and is_valid_box(board)

def is_valid(board, row, col, num):
    # Check if the number is in the current row or column
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False
    # Check if the number is in the current 3x3 grid
    start_row, start_col = row - row % 3, col - col % 3
    for i in range(3):
        for j in range(3):
            if board[i + start_row][j + start_col] == num:
                return False

    return True

def find_empty_cell(board):
    #finds the next empty cell in the board
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                return (i, j)
    return None

def solve_sudoku_csp_backtracking(board):
    # Solve the sudoku board using csp backtracking for each cell
    empty_cell = find_empty_cell(board)
    if not empty_cell:
        return True
    row, col = empty_cell

    for num in range(1, 10):
        if is_valid(board, row, col, num): #checks if the number is valid in the current cell first
            board[row][col] = num
            global nodes
            nodes = nodes + 1
            if solve_sudoku_csp_backtracking(board): #backtracks if the board is not valid
                return True
            board[row][col] = 0

    return False

def solve_sudoku_bruteforce(board):
    # Solve the sudoku board using brute force for each cell and each combination
    empty_cell = find_empty_cell(board)
    if not empty_cell:
        return True
    row, col = empty_cell

    for num in range(1, 10):
        board[row][col] = num
        global nodes
        nodes = nodes + 1
        if solve_sudoku_bruteforce(board) and is_valid_board(board): #checks if the board is valid after each combination then backtracks if not
            return True
        board[row][col] = 0

    return False

def get_legal_values(board, row, col): #gets all the legal values for the current cell
    return {value for value in range(1, 10) if is_valid(board, row, col, value)}

def get_all_legal_values(board): #gets all the legal values for the entire board
    legal_values = defaultdict(dict)
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                legal_values[row][col] = get_legal_values(board, row, col)
    return legal_values

def mrv_cell(legal_values): #gets the cell with the least legal values
    min_remaining = float('inf')
    mrv_cell = None

    for row in legal_values:
        for col in legal_values[row]:
            if len(legal_values[row][col]) < min_remaining:
                min_remaining = len(legal_values[row][col])
                mrv_cell = (row, col)

    return mrv_cell

def update_legal_values(legal_values, row, col, value): #updates the legal values for the current cell and the rest of the board
    updated_legal_values = deepcopy(legal_values)

    del updated_legal_values[row][col]

    if not updated_legal_values[row]:
        del updated_legal_values[row]
    # Update legal values for the current row
    for i in range(9):
        if i != row and col in updated_legal_values[i]:
            updated_legal_values[i][col].discard(value)
            if not updated_legal_values[i][col]:
                return None
    # Update legal values for the current column
        if i != col and row in updated_legal_values and i in updated_legal_values[row]:
            updated_legal_values[row][i].discard(value)
            if not updated_legal_values[row][i]:
                return None
    # Update legal values for the current 3x3 grid
    start_row, start_col = row - row % 3, col - col % 3
    for i in range(3):
        for j in range(3):
            r, c = start_row + i, start_col + j
            if r != row and c != col and r in updated_legal_values and c in updated_legal_values[r]:
                updated_legal_values[r][c].discard(value)
                if not updated_legal_values[r][c]:
                    return None

    return updated_legal_values

def solve_sudoku_forwardchecking_with_heuristics(board, legal_values): #solves the board using forward checking and heuristics
    empty_cell = find_empty_cell(board)
    if not empty_cell:
        return True
    row, col = empty_cell

    row, col = mrv_cell(legal_values)
    
    for value in legal_values[row][col]:
        if is_valid(board, row, col, value): 
            board[row][col] = value
            global nodes
            nodes = nodes + 1
            updated_legal_values = update_legal_values(legal_values, row, col, value) 

            if updated_legal_values is not None:
                if solve_sudoku_forwardchecking_with_heuristics(board, updated_legal_values): #backtracks if the board is not valid
                    return True

            board[row][col] = 0

    return False
    

def print_details(modeName):
    print("Beluonwu, Pearl Chidera, A20444304 solution:")
    print("Input file: ", filename)
    print("Algorithme name: ", modeName)
    print("Input Puzzle: \n")
    print(printedBoard)
    

def start_mode():
    if mode == "1":
        print_details("Brute Force")
        start = time.time()
        solve_sudoku_bruteforce(board)
        end = time.time()
        print("\nNumber of search tree nodes generated: ", nodes)
        print("Search time: ", end - start)

        print("\nSolved Sudoku Puzzle: \n")
        print(board)

    elif mode == "2":
        print_details("CSP Backtracking")
        start = time.time()
        solve_sudoku_csp_backtracking(board)
        end = time.time()
        print("\nNumber of search tree nodes generated: ", nodes)
        print("Search time: ", end - start)

        print("\nSolved Sudoku Puzzle: \n")
        print("\n", board)

    elif mode == "3":
        print_details("CSP Forward Checking with heuristics")
        start = time.time()
        legal_values = get_all_legal_values(board)
        solve_sudoku_forwardchecking_with_heuristics(board, legal_values)
        end = time.time()
        print("\nNumber of search tree nodes generated: ", nodes)
        print("Search time: ", end - start)

        print("\nSolved Sudoku Puzzle: \n")
        print("\n", board)
    elif mode == "4":
        print_details("Checkig board validity")
        if is_valid_board(board):
            print("This is a valid sudoku board.")
        else:
            print("This is an invalid sudoku board.")
    else:
        print("ERROR: Invalid mode.\n")

if n == 3:
    filename = sys.argv[1]
    mode = sys.argv[2]

    load_board()
    
else:
    print("ERROR: Not enough or too many input arguments.\n")
    

