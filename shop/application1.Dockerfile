FROM bde2020/spark-python-template:latest

# ENV SPARK_APPLICATION_PYTHON_LOCATION /app/twitter.py
CMD [ "python3", "/app/main.py" ]
