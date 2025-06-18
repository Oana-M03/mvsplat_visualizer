from flask import Flask, request, Response, send_file
from flask_cors import CORS
import gc
import json
import io

from custom_visualizer.backbone.helpers import get_data, load_all_images, get_video, get_number_scenes

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

def generate_images(new_scene_id):

    response = images[new_scene_id]

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

    new_scene_id = data['scene_idx']

    images = generate_images(new_scene_id)

    img_id = data['img_idx'] % len(images)
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

    response = send_file(path, mimetype='video/mp4')
    response.headers['Access-Control-Allow-Origin'] = '*'

    return response

@app.route('/no-scenes', methods=['GET'])
def get_how_many_scenes():
    gc.collect()

    response = get_number_scenes()

    return Response(json.dumps({'message': response}), mimetype='application/json')


if __name__ == "__main__":

    images = load_all_images()

    app.run()
