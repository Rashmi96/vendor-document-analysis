# Use the official lightweight Python image
FROM python:3.9-slim-buster

# Install OpenJDK 11
RUN apt-get update && \
    apt-get install -y openjdk-11-jdk && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY Requirements.txt .

# Install the Python dependencies
RUN pip uninstall PyMuPDF

RUN pip install --no-cache-dir -r Requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Expose the port the app runs on
EXPOSE 8080

# Define the command to run the application
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
