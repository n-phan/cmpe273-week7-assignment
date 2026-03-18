FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default command; docker-compose.yml overrides this for registry/service/client
CMD ["python", "registry.py"]

