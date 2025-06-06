from flask import Flask, request, jsonify
from flask_cors import CORS
import gc

from helpers import get_data

app = Flask(__name__)
CORS(app)

@app.route('/data', methods=['POST'])
def receive_message():
    gc.collect() # Hangle garbage collection to avoid process being killed 
    data = request.get_json()
    print("Received data:", data)
    # Do something with the data...
    response = get_data()
    return jsonify(response)

if __name__ == "__main__":
    app.run()
