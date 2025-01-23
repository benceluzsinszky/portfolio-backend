FROM python:3.12.1

WORKDIR /app

COPY ./requirements.txt /app
RUN pip install -r requirements.txt

COPY ./api /app/api
COPY ./db /app/db
COPY .env /app

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
