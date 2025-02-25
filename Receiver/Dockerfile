FROM ubuntu:20.04
LABEL maintainer="email"
RUN apt-get update -y && \
    apt-get install -y python3 python3-pip
# Copy requirements and install dependencies
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# Copy wait-for-it.sh
COPY wait-for-it.sh /usr/local/bin/wait-for-it
RUN chmod +x /usr/local/bin/wait-for-it

# Copy application files
COPY . /app
ENTRYPOINT [ "python3" ]
CMD [ "app.py" ]
