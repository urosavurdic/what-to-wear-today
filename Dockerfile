FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Keys are passed in at run time, e.g.
#   docker run --rm -it --env-file .env what-to-wear-today
CMD ["python", "main.py"]
