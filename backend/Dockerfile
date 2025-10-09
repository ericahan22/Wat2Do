# Use official Python runtime as base image
# Use ARM64 architecture (native for M4 Mac Mini)
FROM --platform=linux/arm64 python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set work directory
WORKDIR /app

# Copy requirements files and wheels directory
COPY requirements.txt .
COPY wheels/ ./wheels/

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Copy and set up entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh && \
    # Ensure Unix line endings and verify the script
    sed -i 's/\r$//' /usr/local/bin/docker-entrypoint.sh && \
    ls -la /usr/local/bin/docker-entrypoint.sh && \
    head -1 /usr/local/bin/docker-entrypoint.sh

# Expose port
EXPOSE 3000

# Use entrypoint script
ENTRYPOINT ["docker-entrypoint.sh"]

