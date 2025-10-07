# Use official Python image
FROM python:3.12-slim

# Set working directory in container
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Set environment variables (you can override them at runtime)
ENV OPENWEATHER_API_KEY=dummy
ENV GROQ_API_KEY=dummy
ENV IPINFO_API_KEY=dummy

# Expose port if you later use a web app
# EXPOSE 8000

# Default command
CMD ["python", "main.py"]