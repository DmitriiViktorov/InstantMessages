FROM python:3.10-slim

WORKDIR /app
ENV PYTHONPATH=/app


RUN apt-get update && apt-get install -y supervisor

COPY requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

COPY ./app /app

#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5050", "--log-level=debug"]
CMD ["/usr/bin/supervisord"]
