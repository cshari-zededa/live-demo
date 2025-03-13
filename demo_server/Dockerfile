FROM dustynv/jetson-inference:r36.3.0

RUN apt update && \
    apt install -y vim git ssh

COPY jetson-inference/data /jetson-inference/data 
COPY jetson-inference/python/training/classification/data /jetson-inference/python/training/classification/data
COPY jetson-inference/python/training/classification/models /jetson-inference/python/training/classification/models
COPY jetson-inference/python/training/detection/ssd/data /jetson-inference/python/training/detection/ssd/data
COPY jetson-inference/python/training/detection/ssd/models /jetson-inference/python/training/detection/ssd/models
#COPY my-recognition.py /opt/jetson-inference/build/aarch64/bin/my-recognition.py

# Create a new user with a password (Change `myuser` and `mypassword` as needed)
RUN useradd -m -s /bin/bash myuser && \
    echo 'myuser:mypassword' | chpasswd && \
    mkdir -p /home/myuser/.ssh && \
    chmod 700 /home/myuser/.ssh

# Configure SSH to allow password authentication
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    echo "PermitRootLogin no" >> /etc/ssh/sshd_config

WORKDIR /jetson-inference 

# Start SSH service
CMD ["bash", "-c", "service ssh start; while true; do sleep 60; done"]
