FROM bde2020/spark-python-template:3.3.0-hadoop3.3

# ne treba jer sam video da se nalazi u base
#COPY /template.sh /
#EXPOSE 3306
ENV SPARK_APPLICATION_PYTHON_LOCATION /app/main.py
#CMD [ "python3", "/app/main.py" ]
