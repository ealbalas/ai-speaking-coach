# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg

# Copy the rest of the application's source code from the host to the image's filesystem.
COPY . .

# Expose the port the app runs on. This will be dynamically set by the hosting environment.
EXPOSE $PORT

# Define the command to run the application.
# It uses the PORT environment variable provided by the hosting service.
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
