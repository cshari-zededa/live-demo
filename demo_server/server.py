from flask import Flask, render_template, send_from_directory, jsonify
import time
import random
import os
import threading

app = Flask(__name__)

# Path to the static folder
STATIC_FOLDER = 'static'

# Initial images and text
images = ["image1.png", "image2.png"]
text = "Initial text from the server."

# Function to update images and text
def update_content():
    global images, text
    while True:
        time.sleep(10)  # Update every 10 seconds
        # Simulate new images and text
        images = [f"image{random.randint(1, 3)}.png" for _ in range(3)]
        text = f"Updated text at {time.ctime()}"

# Start the content update thread
update_thread = threading.Thread(target=update_content)
update_thread.daemon = True
update_thread.start()

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5085)
