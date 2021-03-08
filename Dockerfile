FROM python:3.8.7-slim-buster

# Non-root user for security purposes.
# Static GID/UID
RUN addgroup --gid 10001 --system app \
	&& adduser --uid 10000 --system --group app --home /home/app

# Install system packages that are considered standard for all Python applications
# Tini allows us to avoid several Docker edge cases, see https://github.com/krallin/tini
RUN apt-get update && apt-get -y --no-install-recommends install \
	# software-properties-common \
    # build-essential \
	tini \
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

# Use an entrypoint to use container as an executable / specify the default container command
ENTRYPOINT ["/usr/bin/tini", "--", "python3"]

# Use the non-root user to run our application
USER app

# Default arguments for your app 
CMD ["/app/main.py", "/app/configs/config.yml"]
