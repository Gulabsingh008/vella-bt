FROM python:3.11-slim  # Changed from 3.9 to 3.11 (3.13 removed imghdr)

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-u", "main.py"]
