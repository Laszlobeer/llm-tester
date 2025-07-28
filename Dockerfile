# Use official Python image
FROM python:3.11-slim-bullseye

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libxcb-xinerama0 \
    libxkbcommon-x11-0 \
    xauth \
    xvfb \
    && rm -rf /var/lib/apt/lists/*



# Install Python dependencies
RUN git clone https://github.com/Laszlobeer/llm-tester
RUN pip install --no-cache-dir \
    PyQt5 \
    requests

# Set environment variables for X11 forwarding (for GUI)
ENV DISPLAY=:0
ENV QT_DEBUG_PLUGINS=0
ENV QT_X11_NO_MITSHM=1

# Start the application with xvfb-run for headless environments
CMD ["xvfb-run", "python", "app.py"]
