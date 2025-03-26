FROM dustynv/jetson-inference:r36.3.0

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && \
    apt install -y vim git ssh

COPY demo_server.py /jetson-inference/demo_server.py 
COPY static /jetson-inference/static
COPY entrypoint.sh /jetson-inference/entrypoint.sh

# Set a root password (change 'yourpassword' to your desired password)
RUN echo 'root:yourpassword' | chpasswd

# Allow root login via SSH with password authentication
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

# Create the SSH directory and set permissions
RUN mkdir /var/run/sshd && \
    chmod 0755 /var/run/sshd

WORKDIR /jetson-inference 

RUN pip3 install fastapi uvicorn[standard]

ENTRYPOINT ["/bin/bash", "entrypoint.sh"]
