from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import tensorflow as tf

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load the trained model
model = tf.keras.models.load_model('../temp/best.weights.h5', compile=False)

# Function to predict the next move
def predict_move(board_state):
    board = np.array(board_state).reshape((1, 20, 20, 1))  # Adjust shape as needed
    policy, value = model.predict(board)
    move = np.argmax(policy)
    return int(move)

@app.route('/move', methods=['POST'])
def get_move():
    data = request.json
    board_state = data['board']
    print('Received board state:', board_state)  # Log the received board state
    move = predict_move(board_state)
    print('Predicted move:', move)  # Log the predicted move
    return jsonify({'move': move})

if __name__ == '__main__':
    app.run(debug=True)
