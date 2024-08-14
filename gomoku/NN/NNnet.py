import argparse
import os
import time
import numpy as np
import sys
import tensorflow as tf

sys.path.append('../..')
from utils import *
from NeuralNet import NeuralNet
from .GomukuNet import GomukuNNet as gomnet
from tensorflow.keras.optimizers import Adam

# Suppress TensorFlow INFO and DEBUG messages
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
tf.get_logger().setLevel('ERROR')

# Arguments for training
args = dotdict({
    'lr': 0.001,           # Learning rate
    'dropout': 0.3,        # Dropout rate
    'epochs': 10,          # Number of epochs
    'batch_size': 64,      # Batch size
    'cuda': True,         # Use CUDA (not applicable for TensorFlow, generally for PyTorch)
    'num_channels': 512,   # Number of channels in convolutional layers
})

class NNetWrapper(NeuralNet):
    def __init__(self, game):
        """
        Initialize the neural network wrapper.

        :param game: The game instance.
        """
        # Initialize the Gomoku neural network
        self.game = game
        self.args = args
        self.nnet = gomnet(game, args)
        self.board_x, self.board_y = game.getBoardSize()  # Board dimensions
        self.action_size = game.getActionSize()           # Size of the action space

    def train(self, examples, use_tf_dataset=False):
        """
        Train the neural network with provided examples.

        :param examples: List of training examples, each example is of form (board, pi, v)
        :param use_tf_dataset: Boolean flag to choose between using tf.data.Dataset or direct NumPy arrays.
        """
        # Unzip examples into separate arrays
        input_boards, target_pis, target_vs = list(zip(*examples))
        input_boards = np.asarray(input_boards)
        target_pis = np.asarray(target_pis)
        target_vs = np.asarray(target_vs)

        if use_tf_dataset:
            # Use tf.data.Dataset for more complex and efficient data handling
            train_dataset = tf.data.Dataset.from_tensor_slices((input_boards, (target_pis, target_vs)))
            train_dataset = train_dataset.shuffle(buffer_size=len(input_boards))  # Shuffle the dataset
            train_dataset = train_dataset.batch(args.batch_size)                 # Batch the dataset
            train_dataset = train_dataset.prefetch(buffer_size=tf.data.experimental.AUTOTUNE)  # Prefetch for efficiency
            train_dataset = train_dataset.repeat()  # Ensure the dataset repeats indefinitely for training

            # Train the model using the dataset
            history = self.nnet.model.fit(train_dataset, epochs=args.epochs, steps_per_epoch=len(input_boards) // args.batch_size)
        else:
            # Use direct NumPy arrays for training
            history = self.nnet.model.fit(x=input_boards, y=[target_pis, target_vs], batch_size=args.batch_size, epochs=args.epochs)

        # Print training history
        print("Training history: ", history.history)

    def predict(self, board):
        """
        Predict the policy and value for a given board state.

        :param board: np array representing the board state.
        :return: tuple (policy, value) where policy is the action probabilities and value is the game outcome.
        """
        # Timing the prediction (optional)
        start = time.time()

        # Prepare the input for the model
        board = board[np.newaxis, :, :]

        # Run the prediction
        pi, v = self.nnet.model.predict(board, verbose=False)

        # Optionally print the time taken for prediction
        # print('PREDICTION TIME TAKEN : {0:03f}'.format(time.time()-start))
        
        return pi[0], v[0]

    def save_checkpoint(self, folder='checkpoint', filename='checkpoint.keras'):
        """
        Save the entire model (architecture + weights) to a checkpoint file.

        :param folder: Directory where the checkpoint will be saved.
        :param filename: Name of the checkpoint file.
        """
        filepath = os.path.join(folder, filename)
        if not os.path.exists(folder):
            print(f"Checkpoint Directory does not exist! Making directory {folder}")
            os.mkdir(folder)
        else:
            print("Checkpoint Directory exists!")
        self.nnet.model.save(filepath)  # Save the entire model (architecture + weights)

    def load_checkpoint(self, folder='checkpoint', filename='checkpoint.keras'):
        """
        Load the entire model (architecture + weights) from a checkpoint file.

        :param folder: Directory where the checkpoint is located.
        :param filename: Name of the checkpoint file.
        """
        filepath = os.path.join(folder, filename)
        if not os.path.exists(filepath):
            raise Exception(f"No model in path {filepath}")
        self.nnet.model = tf.keras.models.load_model(filepath, compile=False)  # Load the entire model (architecture + weights)
        # Compile the model after loading
        self.nnet.model.compile(loss=['categorical_crossentropy', 'mean_squared_error'], optimizer=Adam(self.args.lr))
