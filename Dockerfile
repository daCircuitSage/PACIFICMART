# Use Python 3.11 slim image for smaller size
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY App/ .

# Expose port
EXPOSE 8001

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]
