# Use Oracle Linux 8 as base image
FROM oraclelinux:8

# Install necessary dependencies
RUN dnf install -y python3 python3-pip

# Install kubectl
RUN curl -LO https://dl.k8s.io/release/v1.24.0/bin/linux/amd64/kubectl \
    && chmod +x ./kubectl \
    && mv ./kubectl /usr/local/bin/kubectl

# Set the working directory to /app
WORKDIR /app

# Copy the Python script into the container
COPY ./ip_tools.py /app/ip_tools.py
COPY data/ip-list.txt /app/ip-list.txt

# The default command (can be overridden at runtime)
CMD ["python3", "/app/ip_tools.py"]