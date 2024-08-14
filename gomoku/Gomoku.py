from __future__ import print_function
import sys
sys.path.append('..')  # Add parent directory to the system path for imports
from Game import Game  # Import the Game base class
from .GomokuLogic import Board  # Import the Board class specific to Gomoku
import numpy as np  # Import NumPy for numerical operations

class GomokuGame(Game):
    # Define a dictionary for square content representation
    square_content = {
        -1: "X",  # Player -1's piece
        +0: "-",  # Empty square
        +1: "O"   # Player +1's piece
    }

    @staticmethod
    def getSquarePiece(piece):
        """
        Static method to get the string representation of a piece.
        :param piece: Piece value (-1, 0, 1)
        :return: String representation of the piece
        """
        return GomokuGame.square_content[piece]

    def __init__(self, n=20):
        """
        Initialize the game with board size n x n.
        :param n: Size of the board (default is 20)
        """
        self.n = n

    def getInitBoard(self):
        """
        Return the initial board state.
        :return: Initial board as a NumPy array
        """
        b = Board(self.n)  # Create a Board instance with size n
        return np.array(b.pieces)  # Return the board pieces as a NumPy array

    def getBoardSize(self):
        """
        Return the dimensions of the board.
        :return: Tuple representing board dimensions (n, n)
        """
        return (self.n, self.n)

    def getActionSize(self):
        """
        Return the number of possible actions.
        :return: Total number of actions (n*n)
        """
        return self.n * self.n

    def getNextState(self, board, player, action):
        """
        Apply an action to the board and return the next state.
        :param board: Current board state
        :param player: Current player (-1 or +1)
        :param action: Action to apply (position on the board)
        :return: Tuple (new board state, next player)
        """
        b = Board(self.n)  # Create a new Board instance
        b.pieces = np.copy(board)  # Copy the current board state
        move = (int(action / self.n), action % self.n)  # Convert action to board coordinates
        b.execute_move(move, player)  # Execute the move
        return (b.pieces, -player)  # Return the new board state and the next player

    def getValidMoves(self, board, player):
        """
        Get a list of valid moves.
        :param board: Current board state
        :param player: Current player (-1 or +1)
        :return: Binary vector of valid moves
        """
        valids = [0] * self.getActionSize()  # Initialize the valid moves list with zeros
        b = Board(self.n)  # Create a new Board instance
        b.pieces = np.copy(board)  # Copy the current board state
        legalMoves = b.get_legal_moves(player)  # Get the legal moves for the player
        for x, y in legalMoves:  # Mark the valid moves
            valids[self.n * x + y] = 1
        return np.array(valids)  # Return the valid moves as a NumPy array

    def getGameEnded(self, board, player):
        """
        Check if the game has ended.
        :param board: Current board state
        :param player: Current player (-1 or +1)
        :return: 0 if not ended, 1 if player 1 won, -1 if player 1 lost
        """
        b = Board(self.n)  # Create a new Board instance
        b.pieces = np.copy(board)  # Copy the current board state
        if b.is_win(player):  # Check if the current player has won
            return 1
        if b.is_win(-player):  # Check if the opponent has won
            return -1
        if not b.has_legal_moves(player) and not b.has_legal_moves(-player):  # Check for a draw
            return 1e-4  # Indicate a draw with a very small positive value to distinguish from no end
        return 0  # Game is not ended

    def getCanonicalForm(self, board, player):
        """
        Return the canonical form of the board.
        :param board: Current board state
        :param player: Current player (-1 or +1)
        :return: Canonical board state
        """
        return player * board

    def getSymmetries(self, board, pi):
        """
        Get symmetrical representations of the board and policy vector.
        :param board: Current board state
        :param pi: Policy vector
        :return: List of symmetrical (board, pi) pairs
        """
        assert(len(pi) == self.n**2)  # Ensure the policy vector has the correct length
        pi_board = np.reshape(pi, (self.n, self.n))  # Reshape the policy vector to match the board
        l = []

        for i in range(1, 5):  # Generate rotations
            for j in [True, False]:  # Generate reflections
                newB = np.rot90(board, i)  # Rotate the board
                newPi = np.rot90(pi_board, i)  # Rotate the policy vector
                if j:
                    newB = np.fliplr(newB)  # Reflect the board
                    newPi = np.fliplr(newPi)  # Reflect the policy vector
                l += [(newB, list(newPi.ravel()))]  # Add the symmetrical pair to the list
        return l

    def stringRepresentation(self, board):
        """
        Get a string representation of the board.
        :param board: Current board state
        :return: String representation of the board
        """
        return board.tostring()

    def stringRepresentationReadable(self, board):
        """
        Get a human-readable string representation of the board.
        :param board: Current board state
        :return: Human-readable string representation of the board
        """
        board_s = "".join(self.square_content[square] for row in board for square in row)  # Convert board to string
        return board_s

    def getScore(self, board, player):
        """
        Get the score for a player.
        :param board: Current board state
        :param player: Player to get the score for (-1 or +1)
        :return: Score of the player
        """
        b = Board(self.n)  # Create a new Board instance
        b.pieces = np.copy(board)  # Copy the current board state
        return b.countDiff(player)  # Get the score for the player

    @staticmethod
    def display(board):
        """
        Display the board in a human-readable format.
        :param board: Current board state
        """
        n = board.shape[0]  # Get the size of the board
        print("   ", end="")
        for y in range(n):  # Print column numbers
            print(y, end=" ")
        print("")
        print("-" * (2 * n + 3))
        for y in range(n):  # Print each row
            print(f"{y:2} |", end="")  # Print the row number
            for x in range(n):
                piece = board[y][x]  # Get the piece to print
                print(GomokuGame.square_content[piece], end=" ")
            print("|")
        print("-" * (2 * n + 3))
