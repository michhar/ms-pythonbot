FROM python:3.5

RUN mkdir /code
WORKDIR /code
ADD . /code/
RUN pip install -r requirements.txt

EXPOSE 3978
CMD ["python", "/code/runserver.py"]