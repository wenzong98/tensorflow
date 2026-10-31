FROM python:3.12-slim
WORKDIR /app
COPY graphcache /app/graphcache
COPY public_tests /app/public_tests
COPY incidents /app/incidents
ENV PYTHONPATH=/app
CMD ["python", "-m", "unittest", "discover", "-s", "/app/public_tests", "-v"]
