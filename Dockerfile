FROM python:3.11-slim

LABEL maintainer="Karl Swanson <karlcswanson@gmail.com>"

# Prevent .pyc file creation and ensure unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=America/Chicago

WORKDIR /usr/src/app

# Set timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install required packages: curl, git, python3-tk (for Tkinter), and Node.js 20 (includes npm)
RUN apt-get update && \
    apt-get install -y curl git python3-tk && \
    curl -sL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy project files into the container
COPY . .

# Upgrade pip and install Python dependencies
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install -r py/requirements.txt

# Install production Node.js dependencies and build frontend assets
RUN npm install --only=prod && npm run build

EXPOSE 8058

CMD ["python3", "py/micboard.py"]