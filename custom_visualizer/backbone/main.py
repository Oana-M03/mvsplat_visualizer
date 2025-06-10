from flask import Flask, request, Response
from flask_cors import CORS
import gc
import json

from custom_visualizer.backbone.helpers import get_data

app = Flask(__name__)
CORS(app)

def generate(options):
    response = get_data(options)
    for batch in response:
        yield json.dumps(batch) + '\n' 

@app.route('/data', methods=['POST'])
def receive_message():
    gc.collect()
    data = request.get_json()
    print("Received data:", data['message'])

    return Response(generate(data['message']), mimetype='application/json')

if __name__ == "__main__":
    app.run()
