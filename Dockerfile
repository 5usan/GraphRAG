FROM python:3.11-slim

LABEL maintainer="Susan Shrestha"
LABEL description="GraphRAG: Retrieval-Augmented Generation for Question Answering over Knowledge Graphs"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip setuptools wheel

COPY requirements.txt .
# Install Python dependencies
RUN pip install -r requirements.txt

# Copy application code
COPY src /app/src

WORKDIR /app/src
# Expose port
EXPOSE 8000

# Default command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]