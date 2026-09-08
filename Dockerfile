# Use a lightweight Python image
FROM python:3.10-slim

# Install Chromium browser and driver for Selenium
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python script
COPY . .

# Command to run the automation robot
CMD ["python", "rpa_agent.py"]
