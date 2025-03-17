FROM dustynv/jetson-inference:r36.3.0

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && \
    apt install -y vim git ssh

COPY demo_server.py /jetson-inference/demo_server.py 
COPY static /jetson-inference/static
COPY entrypoint.sh /jetson-inference/entrypoint.sh

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

RUN pip3 install fastapi uvicorn[standard]

ENTRYPOINT ["/bin/bash", "entrypoint.sh"]
