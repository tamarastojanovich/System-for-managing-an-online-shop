from pyspark.sql import SparkSession
import os, json
from pyspark.sql.functions import column
PRODUCTION = True if ("PRODUCTION" in os.environ) else False
DATABASE_IP = os.environ["DATABASE_IP"] if ( "DATABASE_IP" in os.environ ) else "localhost"

builder = SparkSession.builder.appName ( "PySpark categories statistics" )

if ( not PRODUCTION ):
    builder = builder.master ( "local[*]" )\
                    .config (
                        "spark.driver.extraClassPath",
                        "mysql-connector-j-8.0.33.jar"
                    )
                    

spark = builder.getOrCreate( )

categories_and_products = spark.read \
    .format ( "jdbc" ) \
    .option ( "driver","com.mysql.cj.jdbc.Driver" ) \
    .option ( "url", f"jdbc:mysql://{DATABASE_IP}/shopInfo" ) \
    .option ( "dbtable", "productCategory" ) \
    .option ( "user", "root" ) \
    .option ( "password", "root" ).load ( )

products_and_orders=spark.read \
    .format ( "jdbc" ) \
    .option ( "driver","com.mysql.cj.jdbc.Driver" ) \
    .option ( "url", f"jdbc:mysql://{DATABASE_IP}/shopInfo" ) \
    .option ( "dbtable", "orderPro" ) \
    .option ( "user", "root" ) \
    .option ( "password", "root" ).load ( )
    
orders=spark.read \
    .format ( "jdbc" ) \
    .option ( "driver","com.mysql.cj.jdbc.Driver" ) \
    .option ( "url", f"jdbc:mysql://{DATABASE_IP}/shopInfo" ) \
    .option ( "dbtable", "orders" ) \
    .option ( "user", "root" ) \
    .option ( "password", "root" ).load ( )
    
    
orders=orders.filter(orders.status=='COMPLETE')

prod=products_and_orders.join(orders,["orderId"])


categories_sorted=categories_and_products.join(prod,["prod"],"full").na.fill(value=0,subset=["quantity"])

cat_sort=categories_sorted.rdd.map(lambda x:(x["category"],x["quantity"])).reduceByKey(lambda x,y:x+y).sortBy(lambda x:(-x[1],x[0]))

result=cat_sort.collect()

podaci = []
for red in result:
    podaci.append(red[0])


print( "|TAMZ|" + json.dumps(podaci) + "|TAMZ|"  )


spark.stop()

