FROM ubuntu:20.04
LABEL maintainer="email"

# Set environment variable to prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Update the package list and install Python 3 and pip
RUN apt-get update -y && \
    apt-get install -y python3 python3-pip locales && \
    # Upgrade pip and setuptools
    pip3 install --upgrade pip setuptools && \
    # Set default locale to avoid potential issues
    locale-gen en_US.UTF-8 && \
    update-locale LANG=en_US.UTF-8

# Copy requirements and install dependencies
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app

# Install dependencies using legacy resolver
RUN pip3 install -r requirements.txt --use-deprecated=legacy-resolver

# Copy wait-for-it.sh
COPY wait-for-it.sh /usr/local/bin/wait-for-it
RUN chmod +x /usr/local/bin/wait-for-it

# Copy application files
COPY . /app

# Set the entrypoint and default command
ENTRYPOINT ["python3"]
CMD ["app.py"]
