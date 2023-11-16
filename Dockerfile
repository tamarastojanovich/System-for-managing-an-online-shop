FROM python:3

COPY korisnici/configuration.py /configuration.py
COPY korisnici/models.py /models.py
COPY korisnici/main.py /main.py
COPY ./requirements.txt /requirements.txt


RUN pip install -r ./requirements.txt

ENTRYPOINT [ "python", "main.py" ]