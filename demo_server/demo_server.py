from flask import Flask, render_template, send_from_directory, jsonify
import time
import random
import os
import threading
import cv2
import requests
import json

app = Flask(__name__)

# Path to the static folder
STATIC_FOLDER = 'static'

# Initial images and text
images = ["image1.png", "image2.png"]
text = "Initial text from the server."

# Global configuration for A/B routing
spray_ratio = [0.4, 0.6]  # Default spray ratio (40% for server1, 60% for server2)
config_url = "http://metadata-server/config"  # URL to fetch the spray ratio config
server1_url = "http://192.168.1.2/inference"
server2_url = "http://192.168.1.2/inference"

# Function to update images and text
def update_content():
    global images, text
    while True:
        time.sleep(10)  # Update every 10 seconds
        # Simulate new images and text
        images = [f"image{random.randint(1, 3)}.png" for _ in range(3)]
        text = f"Updated text at {time.ctime()}"

# Serve the webpage
@app.route('/')
def index():
    return render_template('index.html', images=images, text=text)

# Endpoint to get updated content
@app.route('/get_content')
def get_content():
    return jsonify({"images": images, "text": text})

# Serve static files
@app.route('/static/<filename>')
def static_files(filename):
    return send_from_directory(STATIC_FOLDER, filename)

def fetch_frames():
    cap = cv2.VideoCapture('/dev/video0')
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        send_to_inference_server(frame)

def send_to_inference_server(frame):
    server_url = select_server()
    _, img_encoded = cv2.imencode('.jpg', frame)
    files = {'image': ('frame.jpg', img_encoded.tobytes(), 'image/jpeg')}
    response = requests.post(server_url, files=files)
    if response.status_code == 200:
        # Process the response if needed
        output_image = response.content
        # ...existing code...
    else:
        print(f"Failed to get response from {server_url}")

def select_server():
    if random.random() < spray_ratio[0]:
        return server1_url
    else:
        return server2_url

def refresh_config():
    global spray_ratio
    while True:
        try:
            response = requests.get(config_url)
            if response.status_code == 200:
                config = response.json()
                spray_ratio[0] = config.get('server1_ratio', 0.4)
                spray_ratio[1] = config.get('server2_ratio', 0.6)
        except Exception as e:
            print(f"Failed to refresh config: {e}")
        time.sleep(60)  # Refresh every 60 seconds


#main 
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5085)
    # Start the content update thread
    update_thread = threading.Thread(target=update_content)
    update_thread.daemon = True
    update_thread.start()

    # Start the inference routing thread 
    frame_thread = threading.Thread(target=fetch_frames)
    frame_thread.start()

    # Start the inference routing thread 
    config_thread = threading.Thread(target=refresh_config)
    config_thread.start()

    #wait for completion 
    frame_thread.join()
    config_thread.join()
    update_thread.join()
