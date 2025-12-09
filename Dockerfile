FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# create non-root user
RUN useradd --create-home appuser

# copy requirements first to leverage docker cache
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy app
COPY src /app/src

ENV PATH="/home/appuser/.local/bin:$PATH"
RUN chown -R appuser:appuser /app
USER appuser

ENV PYTHONPATH=/app/src:/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
