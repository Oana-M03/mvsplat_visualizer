from flask import Flask, request, Response
from flask_cors import CORS
import gc
import json
import io

from custom_visualizer.backbone.helpers import get_data, get_images, get_video

app = Flask(__name__)
CORS(app)

images = None

def generate_gaussians(options):
    response = get_data(options)
    for batch in response:
        yield json.dumps(batch) + '\n' 

@app.route('/gaussians', methods=['POST'])
def get_gaussians():
    gc.collect()
    data = request.get_json()
    print("Received data:", data['message'])

    return Response(generate_gaussians(data['message']), mimetype='application/json')

def generate_images():
    response = get_images()

    imglist = []

    for image in response:
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG')
        buffer.seek(0)
        imglist.append(buffer.getvalue())

    return imglist

@app.route('/images', methods=['POST'])
def get_images_endpoint():
    gc.collect()
    data = request.get_json()
    print("Received data:", data)

    img_id = data['index'] % len(images)

    img = images[img_id]

    return Response(img, 
                    mimetype='image/jpeg', 
                    headers={
                        'Content-type': 'image/jpeg', 
                        'Access-Control-Allow-Origin': '*'})

@app.route('/video', methods=['POST'])
def get_video_endpoint():
    gc.collect()
    data = request.get_json()
    print("Received data: ", data['message'])

    path = get_video(data['message'])

    return Response(json.dumps({'message': path}), mimetype='application/json')

if __name__ == "__main__":

    images = generate_images()

    app.run()
