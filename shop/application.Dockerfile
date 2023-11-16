FROM python:3



COPY ./configuration.py /configuration.py
COPY ./model.py /model.py
COPY ./owner.py /owner.py
COPY ./shop.py /shop.py
COPY ./courier.py /courier.py
COPY ./ownerdecorator.py /ownerdecorator.py

COPY ./requirements.txt /requirements.txt

RUN pip install -r ./requirements.txt

ENTRYPOINT [ "python", "main.py" ]