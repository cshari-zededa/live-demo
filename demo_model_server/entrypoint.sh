#!/bin/bash

# Start SSH service
service ssh start
while true; do python3 infer.py; sleep 10; done
