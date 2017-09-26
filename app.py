from datetime import datetime
import time
from flask import Flask, abort, flash, redirect, render_template, request, url_for, jsonify, send_file
import base64
import json
import sqlite3
import pickle
import os

app = Flask(__name__)
app.config['DEBUG'] = True

ANNOTATORS = ['jmathai']

def get_image_list(annotator):
    IMG_PATH = os.path.join(app.static_folder, 'images/' + annotator)
    if os.path.exists(IMG_PATH):
        files = os.listdir(IMG_PATH)
        return ['http://localhost:5000/static/images/{}/{}'.format(annotator, f) for f in files]
    else:
        return []

@app.route("/<user>")
def home(user):
    if user in ANNOTATORS:
        return render_template('via.html', annotator=user, image_list=get_image_list(user))
    else:
        return abort(404)

@app.route("/<user>/save", methods=['POST'])
def save(user):
    ANNOTATION_DIR = os.path.join(app.static_folder, 'annotations/' + user)
    annotations = request.get_json()
    annotation_file_name = user + '_annotations_' + time.strftime("%Y_%m_%d_%H:%M:%S", time.localtime()) + '.json'
    annotation_file_path = os.path.join(ANNOTATION_DIR, annotation_file_name)
    with open(annotation_file_path, 'w') as handle:
        json.dump(annotations, handle)
    return "annotations saved."

@app.route("/images/<user>/<img_file>")
def get_image(img_file):
    return send_file(request.path)

@app.route("/<user>/load")
def load(user):
    ANNOTATION_DIR = os.path.join(app.static_folder, 'annotations/' + user)
    files = os.listdir(ANNOTATION_DIR)
    last_saved_file = sorted(files, reverse=True)[0]
    last_saved_path = os.path.join(ANNOTATION_DIR, last_saved_file)
    print('last_saved_file', last_saved_path)
    try:
        with open(last_saved_path, 'r') as handle:
            annotations = json.load(handle)
    except:
        print('No pickle found!!!')
        annotations = {}
    return jsonify(annotations)

@app.route('/annotations', defaults={'req_path': ''})
@app.route('/annotations/<path:req_path>')
def dir_listing(req_path):
    BASE_DIR = os.path.join(app.static_folder, 'annotations')
    # Joining the base and the requested path
    abs_path = os.path.join(BASE_DIR, req_path)

    # Return 404 if path doesn't exist
    print(abs_path)
    if not os.path.exists(abs_path):
        return abort(404)

    # Check if path is a file and serve
    if os.path.isfile(abs_path):
        return send_file(abs_path)

    # Show directory contents
    files = os.listdir(abs_path)
    if req_path is '': req_path = 'annotations'
    files = [os.path.join(req_path, f) for f in files]
    return render_template('files.html', files=files)

if __name__ == '__main__':
    app.run()
