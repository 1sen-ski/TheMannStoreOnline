FROM python:3

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# / - root directory (c:\)
# WORKDIR /app -> mkdir /app && cd /app
WORKDIR /app

COPY requirements.txt /app/
# Result: /app/requirements.txt

RUN pip install -r requirements.txt

COPY manage.py /app/manage.py
COPY templates /app/templates
COPY static_files /app/static_files
COPY ecommerce /app/ecommerce