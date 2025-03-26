import time
import random
import os
import threading
import cv2
import requests
import json
import base64
import shutil
import asyncio
import uvicorn

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect

app = FastAPI()

# Serve static files (HTML, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initial images and text
images = ["image1.jpg", "image2.jpg"]

STATIC_FOLDER = "static"
OUTPUT_FOLDER = "static"

# Global configuration for A/B routing
spray_ratio = [0.4, 0.6]  # Default spray ratio (40% for server1, 60% for server2)
# URL to fetch the spray ratio config
patch_description_url="http://169.254.169.254/eve/v1/patch/description.json"
server1_url = "http://192.168.1.3:5090/infer_model_a"
server2_url = "http://192.168.1.3:5090/infer_model_b"
text = f"Inference request distribution ratio: {spray_ratio[0]*100} : {spray_ratio[1]*100}"
ws_url = os.getenv("WS_URL", "ws://default-host:5085/ws")  # Default value if not set
initial_ws_url = ws_url 

# Endpoint to serve the HTML page
@app.get("/")
async def get():
    with open('static/index.html', 'r') as file:
        content = file.read()
    return HTMLResponse(content=content)


@app.get("/config")
async def get_config():
    return {"ws_url": ws_url}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            #print("serving")
            image1_data = read_image('static/image1.jpg')
            image2_data = read_image('static/image2.jpg')
            await websocket.send_json({"image1": image1_data, "image2": image2_data, "dynamic_text": text})
            await asyncio.sleep(0.1)  # Adjust the delay as needed
    except WebSocketDisconnect:
        pass

def read_image(file_path):
    with open(file_path, "rb") as image_file:
        return image_file.read().hex()

async def fetch_frames():
    cap = cv2.VideoCapture('/dev/video0')
    if not cap.isOpened():
        print("Error: Could not open video device.")
        return
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Warning: Could not read frame from video device.")
            time.sleep(1)  # Add a small delay before retrying
            continue
        #print("Successfully captured frame from webcamera")
        send_to_inference_server(frame)
        await asyncio.sleep(0.1)  # Adjust the delay as needed

def send_to_inference_server(frame):
    server_url, image_file_name = select_server()
    _, img_encoded = cv2.imencode('.jpg', frame)
    files = {'file': ('frame.jpg', img_encoded.tobytes(), 'image/jpeg')}
    #print("sending request")
    try:
        response = requests.post(server_url, files=files, timeout=(1,1))
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
        return
    #print("receiving response")
    if response.status_code == 200:
        # Ensure the directory exists
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        output_path = os.path.join(OUTPUT_FOLDER, 'output.jpg')
          # Save the output image file from the response
        with open(output_path, 'wb') as f:
            f.write(response.content)

        # Rename the output file to image1.jpg
        final_path = os.path.join(STATIC_FOLDER, image_file_name)
        shutil.move(output_path, final_path)
    else:
        print(f"Failed to get response from {server_url}, {response.json()}")

def select_server():
    if random.random() < spray_ratio[0]:
        #print(f"selecting {server1_url}")
        return server1_url, "image1.jpg"
    else:
        #print(f"selecting {server2_url}")
        return server2_url, "image2.jpg"

async def refresh_config():
    global spray_ratio
    global text 
    global ws_url 
    print("Starting periodic refresh of AB routing config")
    while True:
        try:
            print("Fetching config")
            response = requests.get(patch_description_url)
            if response.status_code == 200:
                config_url = response.json()[0]['BinaryBlobs'][0]['url']
                response = requests.get(config_url)
                if response.status_code == 200:
                    encoded_content = response.content
                    decoded_content = base64.b64decode(encoded_content).decode('utf-8')
                    print(decoded_content)
                    config = json.loads(decoded_content)
                    print(config)
                    spray_ratio[0] = config.get('modelA', 40) / 100
                    spray_ratio[1] = config.get('modelB', 60) / 100
                    ws_url = config.get('ws_url', initial_ws_url)
                    text = f"Inference request distribution ratio: {spray_ratio[0]*100}, {spray_ratio[1]*100}"
                else:
                    print(response)
            else:
                print(response)

        except Exception as e:
            print(f"Failed to refresh config: {e}")
        await asyncio.sleep(5)  # Adjust the delay as needed


def run_uvicorn():
    uvicorn.run(app, host="0.0.0.0", port=5085)

async def main():
    # Start Uvicorn in a separate thread
    thread = threading.Thread(target=run_uvicorn, daemon=True)
    thread.start()

    # Keep the event loop running
    await asyncio.gather(fetch_frames(), refresh_config())

asyncio.run(main())
