FROM python:3.11-slim

WORKDIR /app

COPY . /app/

RUN pip install numpy pandas requests schedule

CMD ["python", "generator.py"]