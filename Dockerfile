FROM python:3.8.7-slim-buster

RUN apt-get update && apt-get -y --no-install-recommends install \
	# software-properties-common \
    # build-essential \
    && apt-get -y autoremove \
    && apt-get clean autoclean

# Install application specific system packages
# RUN apt-get install -y PACKAGE

RUN pip install --upgrade pip

# Copy and install third party dependencies
# packages, thus the two COPY / RUN statement pairs should speed up rebuilds
COPY ./third_party/requirements.txt /third_party/requirements.txt
RUN pip install -r /third_party/requirements.txt


# Copy and install other repos
COPY ./third_party /third_party

# Copy the current directory contents into the container at /app
COPY . /app/

# Set the working directory to /app
WORKDIR /app

RUN apt-get update && apt-get install -y python3-tk
RUN pip install jupyter
RUN pip install voila

# Default arguments for your app
CMD ["/bin/bash"]
