FROM python:3.12-slim

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libssl-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# --- Fix for legacy packages that still `import pkg_resources` at build time ---
# setuptools>=81 removed pkg_resources, which breaks openai-whisper's old-style
# setup.py during "Getting requirements to build wheel".
# 1) Pin setuptools to a version that still ships pkg_resources.
# 2) Install openai-whisper with --no-build-isolation so pip reuses THIS
#    setuptools instead of downloading the newest one into an isolated env.
RUN pip install --no-cache-dir "setuptools<81" wheel
RUN pip install --no-cache-dir --no-build-isolation openai-whisper==20231117

# Install the rest of the Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create logs directory
RUN mkdir -p logs data

# Environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Run
CMD ["python", "main.py"]