FROM python:3.9
EXPOSE 8082
WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./order_api_test.py /code/app.py
COPY gunicorn_conf_api.py /code/gunicorn_conf.py

#CMD ["gunicorn", "--conf", "gunicorn_conf.py", "--bind", "0.0.0.0:80", "app.main:app"]
CMD ["gunicorn", "-c", "gunicorn_conf.py","--bind", "0.0.0.0:8082", "app:app"]
