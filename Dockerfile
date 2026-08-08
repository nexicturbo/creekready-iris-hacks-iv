FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

RUN addgroup --system creekready \
    && adduser --system --ingroup creekready creekready

COPY --chown=creekready:creekready . .

USER creekready
EXPOSE 8000

CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]
