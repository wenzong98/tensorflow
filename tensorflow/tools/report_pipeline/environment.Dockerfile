FROM python:3.12-slim
WORKDIR /app
COPY tensorflow/python/eager/plan_runtime /app/plan_runtime
COPY tensorflow/tools/report_pipeline/history_replay.py /app/incidents/history_replay.py
ENV PYTHONPATH=/app PYTHONDONTWRITEBYTECODE=1
CMD ["python", "/app/incidents/history_replay.py"]
