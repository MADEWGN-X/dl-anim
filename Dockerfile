# Use the official Python image from the Docker Hub
FROM python:3.11-alpine

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Install dependencies
RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    libxml2-dev \
    libxslt-dev \
    ffmpeg \
    && pip install --upgrade pip

# Create and set the working directory
WORKDIR /usr/src/app

# Copy the requirements file
COPY requirements.txt ./

# Install the required Python packages
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .
EXPOSE 8000
# Run the bot
CMD ["echo done"]

CMD ["python", "main.py"]

