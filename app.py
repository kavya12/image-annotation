import os
import time
from datetime import datetime
import base64
import json
import sqlite3
import pickle
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, abort, flash, redirect, render_template, request, url_for, jsonify, send_file


app = Flask(__name__)
app.config['DEBUG'] = True


ANNOTATORS = ['jmathai']
APP_URL = "http://localhost:5000" 

def get_image_list(annotator):
    '''
    Return a list of URIs for the images.
    '''
    IMG_PATH = os.path.join(app.static_folder, 'images/' + annotator)
    if os.path.exists(IMG_PATH):
        files = os.listdir(IMG_PATH)
        return [APP_URL + '/static/images/{}/{}'.format(annotator, f) for f in files]
    else:
        app.logger.error('IMG_PATH:%s doesn\'t exist', IMG_PATH)
        return []

def get_annotation_attributes(annotator):
	'''
	Return a list of attributes to be annotated by the user.
	'''
	ANNOT_ATTRIBUTES_FILE = os.path.join(app.static_folder, 'attributes/' + annotator + '/list_of_attributes.txt')
	
	with open(ANNOT_ATTRIBUTES_FILE, 'r') as af:
		return [line.strip() for line in af.readlines()]

		
@app.route("/<user>")
def home(user):
    if user in ANNOTATORS:
        image_list = get_image_list(user)
        attributes_list = get_annotation_attributes(user)

        if not image_list:
            app.logger.error('Image list not obtained for user:%s', user)
            return 'No images allotted. \nContact Admin.', 500
			
        if not attributes_list:
            app.logger.error('Annotation attributes list not obtained for user:%s', user)
            return 'No annotation attributes allotted. \nContact Admin.', 500
			
        return render_template('via.html', annotator=user, image_list=get_image_list(user), flask_app_url=APP_URL, attributes_list = get_annotation_attributes(user))
    else:
        app.logger.error('User:%s not in the annotator list', user)
        return abort(404)

@app.route("/<user>/save_changes", methods=["POST"])
def save_changes(user):
    ANNOTATION_DIR = os.path.join(app.static_folder, 'annotations/' + user)
    annotations = request.get_json()
    f = annotations['filename'].split('/')[-1]
    file_ext = f.split('.')[-1]
    annotation_file_name = f.replace(file_ext, 'json')
    annotation_file_path = os.path.join(ANNOTATION_DIR, annotation_file_name)
    try:
        with open(annotation_file_path, 'w') as handle:
            json.dump({annotations['filename']:annotations}, handle)
    except:
        app.logger.error('save changes(file_path:%s) request received for user:%s failed', annotation_file_path, user)
        return "Save changes failed", 500
    return "Saved changes.", 200

@app.route("/<user>/save", methods=['POST'])
def save(user):
    ANNOTATION_DIR = os.path.join(app.static_folder, 'annotations/' + user)
    annotations = request.get_json()
    annotation_file_name = user + '_annotations_' + time.strftime("%Y_%m_%d_%H:%M:%S", time.localtime()) + '.json'
    annotation_file_path = os.path.join(ANNOTATION_DIR, annotation_file_name)
    try:
        with open(annotation_file_path, 'w') as handle:
            json.dump(annotations, handle)
    except:
        app.logger.error('save (file_path:%s) request received for user:%s failed', annotation_file_path, user)
        return 'Annotation save failed.', 500
    return "Annotations saved.", 200

@app.route("/images/<user>/<img_file>")
def get_image(img_file):
    return send_file(request.path)

@app.route("/<user>/load")
def load(user):
    ANNOTATION_DIR = os.path.join(app.static_folder, 'annotations/' + user)
    files = os.listdir(ANNOTATION_DIR)
    annotations = {}
    try:
        for f in files:
            f_path = os.path.join(ANNOTATION_DIR, f)
            with open(f_path, 'r') as handle:
                f_annotations = json.load(handle)
            for k, v in f_annotations.items():
                annotations[k] = v
    except:
        app.logger.error('load annotations(file_path:%s) for user:%s failed', ANNOTATION_DIR, user)
        return 'load failed', 500
    return jsonify(annotations)

@app.route('/annotations', defaults={'req_path': ''})
@app.route('/annotations/<path:req_path>')
def dir_listing(req_path):
    BASE_DIR = os.path.join(app.static_folder, 'annotations')
    # Joining the base and the requested path
    abs_path = os.path.join(BASE_DIR, req_path)

    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        app.logger.error('annotation path(%s) doesn\'t exist', abs_path)
        return abort(404)

    # Check if path is a file and serve
    if os.path.isfile(abs_path):
        return send_file(abs_path)

    # Show directory contents
    files = os.listdir(abs_path)
    if req_path is '':
        req_path = 'annotations'
    files = [os.path.join(req_path, f) for f in files]
    return render_template('files.html', files=files)

if __name__ == '__main__':
    handler = RotatingFileHandler('image-annotation.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.logger.info("USING APP_URL:%s", APP_URL)
    app.run()
