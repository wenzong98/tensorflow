FROM python:3.12-slim
WORKDIR /app
COPY graphcache /app/graphcache
COPY incidents /app/incidents
ENV PYTHONPATH=/app PYTHONDONTWRITEBYTECODE=1
CMD ["python", "/app/incidents/customer_history.py"]
