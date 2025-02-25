FROM ubuntu:20.04
LABEL maintainer="ikim59@my.bcit.ca"

# Set environment variable to prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Update the package list and install Python 3 and pip
RUN apt-get update -y && \
    apt-get install -y python3 python3-pip locales && \
    pip3 install --upgrade pip setuptools && \
    # Set default locale to avoid potential issues
    locale-gen en_US.UTF-8 && \
    update-locale LANG=en_US.UTF-8

# Copy requirements and install dependencies
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN python3 -m pip install -r requirements.txt

# Copy application files
COPY . /app

# Set the entrypoint and default command
ENTRYPOINT ["python3"]
CMD ["app.py"]
