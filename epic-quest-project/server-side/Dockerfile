# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Create and activate a virtual environment
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Upgrade pip to the latest version
RUN pip install --upgrade pip

# Install Flask within the virtual environment
RUN pip install Flask

# Copy the application code into the container
COPY main.py .

# Set the entry command to run the application
CMD ["python", "main.py"]