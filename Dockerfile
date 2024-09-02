FROM python:3.10
WORKDIR /code
EXPOSE 5555
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app
COPY .env .env

CMD ["fastapi", "run", "app/app.py", "--port", "5555"]