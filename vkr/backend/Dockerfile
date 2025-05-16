FROM python:3.13

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# root
RUN groupadd -g 1000 celery && \
    useradd -u 1000 -g celery -s /bin/bash celery && \
    chown -R celery:celery /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

RUN mkdir -p /app/celerybeat && \
    chown -R celery:celery /app

CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]
