"""
Author: Hao Zhou
Date: 09/2024
Board class for Gomoku.
Board data:
  1=white, -1=black, 0=empty
"""

class Board:

    # List of all 4 possible directions on the board for checking win condition, represented as (x, y) offsets
    __directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

    def __init__(self, n):
        """
        Initialize the board with the given size n.
        :param n: Size of the board (n x n)
        """
        self.n = n
        # Create an empty board array
        self.pieces = [[0] * self.n for _ in range(self.n)]

    def __getitem__(self, index):
        """
        Allow the use of the board with [][] indexer syntax.
        :param index: Index of the board
        :return: Board row at the given index
        """
        return self.pieces[index]

    def get_legal_moves(self, color):
        """
        Get all the legal moves for the given color.
        :param color: Color of the player (1 for white, -1 for black)
        :return: List of all legal moves as (x, y) tuples
        """
        moves = []
        # Any empty square is a legal move
        for y in range(self.n):
            for x in range(self.n):
                if self[x][y] == 0:
                    moves.append((x, y))
        return moves

    def has_legal_moves(self, color):
        """
        Check if there are any legal moves for the given color.
        :param color: Color of the player (1 for white, -1 for black)
        :return: True if there are legal moves, False otherwise
        """
        return any(self[x][y] == 0 for x in range(self.n) for y in range(self.n))

    def execute_move(self, move, color):
        """
        Perform the given move on the board.
        :param move: (x, y) tuple representing the move
        :param color: Color of the piece to play (1 for white, -1 for black)
        """
        x, y = move
        self.pieces[x][y] = color

    def is_win(self, color):
        """
        Check if the given color has won the game.
        :param color: Color of the player (1 for white, -1 for black)
        :return: True if the player has won, False otherwise
        """
        for y in range(self.n):
            for x in range(self.n):
                if self[x][y] == color:
                    for direction in self.__directions:
                        if self._check_direction((x, y), direction, color):
                            return True
        return False

    def _check_direction(self, origin, direction, color):
        """
        Check if there are five consecutive pieces in a given direction.
        :param origin: (x, y) tuple representing the starting square
        :param direction: (dx, dy) tuple representing the direction of movement
        :param color: Color of the pieces to check (1 for white, -1 for black)
        :return: True if there are five consecutive pieces, False otherwise
        """
        x, y = origin
        dx, dy = direction
        count = 0

        for _ in range(5):
            if 0 <= x < self.n and 0 <= y < self.n and self[x][y] == color:
                count += 1
                if count == 5:
                    return True
            else:
                break
            x += dx
            y += dy

        return False
