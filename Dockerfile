FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    unixodbc \
    unixodbc-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the project
COPY . .

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install --no-cache-dir -r "Backend-API (Fast API or Flask) [Shared (integration team)]/requirements.txt"

# Change into backend folder
WORKDIR "/app/Backend-API (Fast API or Flask) [Shared (integration team)]"
# Hugging Face port
EXPOSE 7860

# Start FastAPI
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]