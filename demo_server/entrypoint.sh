#!/bin/bash

# Start SSH service
service ssh start
python3 demo_server.py
while true; do sleep 10; done
