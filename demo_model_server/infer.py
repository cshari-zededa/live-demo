#!/usr/bin/env python3
#
# Copyright (c) 2019, NVIDIA CORPORATION. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

from jetson_inference import imageNet
from jetson_utils import loadImage, cudaFont, videoOutput
import os
import sys
from flask import Flask, request, send_file, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Directory to save uploaded images
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
font = cudaFont()

# Allowed extensions for file uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

net1 = imageNet("googlenet")
net2 = imageNet("googlenet") 

models = [net1, net2]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def infer(input_file, net):
    # load an image (into shared CPU/GPU memory)
    img = loadImage(input_file)

    # classify the image
    class_idx, confidence = net.Classify(img)

    # find the object description
    classLabel = net.GetClassDesc(class_idx)

    # print out the result
    print("image is recognized as '{:s}' (class #{:d}) with {:f}% confidence".format(classLabel, class_idx, confidence * 100))

    font.OverlayText(img, text=f"{confidence:05.2f}% {classLabel}", 
                    x=5, y=5 + (font.GetSize() + 5),
                    color=font.White, background=font.Gray40)

    output_file = os.path.join(OUTPUT_FOLDER, os.path.basename(input_file))
    output = videoOutput(output_file, argv=sys.argv)
    output.Render(img)
    return output_file

@app.route('/infer_model_a', methods=['POST'])
def infer_image_model_a():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        input_file = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_file)

        # Perform inference
        output_file = infer(input_file, models[0])

        return send_file(output_file, mimetype='image/png')
    else:
        return jsonify({'error': 'File type not allowed'}), 400

@app.route('/infer_model_b', methods=['POST'])
def infer_image_model_b():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        input_file = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_file)

        # Perform inference
        output_file = infer(input_file, models[1])

        return send_file(output_file, mimetype='image/png')
    else:
        return jsonify({'error': 'File type not allowed'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5090)


