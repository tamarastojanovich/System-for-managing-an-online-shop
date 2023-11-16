from flask import Flask
from flask import request
from collections import OrderedDict

application = Flask ( __name__ )

import os
import subprocess, json
@application.route ( "/product_statistics",methods=["GET"] )
def pro( ):
    os.environ["SPARK_APPLICATION_PYTHON_LOCATION"] = "/app/spark_products.py"
    os.environ["SPARK_SUBMIT_ARGS"] = "--driver-class-path /app/mysql-connector-j-8.0.33.jar --jars /app/mysql-connector-j-8.0.33.jar"
     
    result = subprocess.check_output ( ["/template.sh"] ).decode()
    ret=result.split("|TAMZ|")[1]
    podaci = json.loads(ret)
    my_dict = [OrderedDict(zip(("name", "sold","waiting"), x)) for x in podaci]
    return {"statistics":my_dict}

@application.route ( "/categories_statistics" )
def cat ( ):
    os.environ["SPARK_APPLICATION_PYTHON_LOCATION"] = "/app/spark_categories.py"
    os.environ["SPARK_SUBMIT_ARGS"] = "--driver-class-path /app/mysql-connector-j-8.0.33.jar --jars /app/mysql-connector-j-8.0.33.jar"
     
    result = subprocess.check_output ( ["/template.sh"] ).decode()
    podaci_str = result.split('|TAMZ|')[1]
    podaci = json.loads(podaci_str)
    
    return {"statistics": podaci}


if ( __name__ == "__main__" ):
    application.run ( host = "0.0.0.0",port=9090)