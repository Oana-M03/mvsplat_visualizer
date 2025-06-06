from flask import Flask, request, Response
from flask_cors import CORS
import gc
import json

from helpers import get_data

app = Flask(__name__)
CORS(app)

def generate():
    response = get_data()
    for batch in response:
        yield json.dumps(batch) + '\n' 

@app.route('/data', methods=['POST'])
def receive_message():
    gc.collect()
    data = request.get_json()
    print("Received data:", data)

    return Response(generate(), mimetype='application/json')

if __name__ == "__main__":
    app.run()
