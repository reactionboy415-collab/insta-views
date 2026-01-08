# 1. Base image (Python 3.10 slim version for faster builds)
FROM python:3.10-slim

# 2. Set working directory
WORKDIR /app

# 3. Install system dependencies for HTTP/2 support
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the application code
COPY . .

# 6. Expose the port Flask runs on
EXPOSE 5000

# 7. Start the application using Gunicorn (Production ready)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
