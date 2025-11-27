FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
# python3-tk: Required for Tkinter GUI
# libgl1, libglib2.0-0: Required for OpenCV
RUN apt-get update && apt-get install -y \
    python3-tk \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir opencv-python pillow

# Copy the project files
COPY . .

# Run the application
CMD ["python", "guy.py"]