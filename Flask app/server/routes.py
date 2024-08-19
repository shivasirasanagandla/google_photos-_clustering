from flask import render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
import os
from server import app
from clustering import cluster
import numpy as np
import shutil

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/upload', methods=['POST'])
def upload():
    if 'files[]' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    files = request.files.getlist('files[]')
    
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
    return jsonify(message="Upload Success"), 200

@app.route('/cluster', methods=['POST'])
def clusters():
    # Perform clustering
    labels , image_paths = cluster(app.config['UPLOAD_FOLDER'])
    # print(labels,image_paths)
    labels_= labels.tolist()
    image_names_= [y.removeprefix("c:\\Users\\Ravi Paliwal\\Desktop\\Flask\\server\\uploads\\") for y in image_paths]
    response_data = {
        'message': 'Success',
        'cluster_labels': labels_,
        'image_names': image_names_
    }
    # Delete contents of UPLOAD_FOLDER after sending response
    shutil.rmtree(app.config['UPLOAD_FOLDER'])
    return jsonify(response_data), 200


