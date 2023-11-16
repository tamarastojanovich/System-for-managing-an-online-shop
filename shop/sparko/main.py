from flask import Flask
from flask import request

application = Flask ( __name__ )

import os
import subprocess
@application.route ( "/product_statistics",methods=["GET"] )
def pro( ):
    os.environ["SPARK_APPLICATION_PYTHON_LOCATION"] = "./spark_products.py"
    os.environ["SPARK_SUBMIT_ARGS"] = "--driver-class-path /app/mysql-connector-j-8.0.33.jar --jars /app/mysql-connector-j-8.0.33.jar"
     
    result = subprocess.check_output ( ['/template.sh'] )
    return result.decode ( )

@application.route ( "/categories_statistics" )
def cat ( ):
    os.environ["SPARK_APPLICATION_PYTHON_LOCATION"] = "/app/spark_categories.py"
    os.environ["SPARK_SUBMIT_ARGS"] = "--driver-class-path /app/mysql-connector-j-8.0.33.jar --jars /app/mysql-connector-j-8.0.33.jar"
     
    result = subprocess.check_output ( ["/template.sh"] )
    return result.decode ( )


if ( __name__ == "__main__" ):
    application.run ( host = "0.0.0.0",port=9090 )