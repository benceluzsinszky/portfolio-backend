FROM python:3.12.1

WORKDIR /app

COPY ./requirements.txt /app
RUN pip install -r requirements.txt

COPY ./api /app
COPY ./db /app

CMD ["fastapi", "run", "--workers=4", "main", "--host", "0.0.0.0", "--port", "8000"]