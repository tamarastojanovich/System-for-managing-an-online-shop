from pyspark.sql import SparkSession
from pyspark.sql.functions import column
import os, json

PRODUCTION = True if ("PRODUCTION" in os.environ) else False
DATABASE_IP = os.environ["DATABASE_IP"] if ( "DATABASE_IP" in os.environ ) else "localhost"
builder = SparkSession.builder.appName ( "PySpark Database example" )

if ( not PRODUCTION ):
    builder = builder.master ( "local[*]" )\
                    .config (
                        "spark.driver.extraClassPath",
                        "mysql-connector-j-8.0.33.jar"
                    )


spark = builder.getOrCreate( )
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

completed_orders=orders.filter(orders.status=='COMPLETE')

waiting_orders=orders.filter(orders.status!='COMPLETE')

delivered_products=products_and_orders.join(completed_orders,["orderId"]).na.fill(value=0,subset=["quantity"]).withColumnRenamed("quantity", "delivered")

waiting_products=products_and_orders.join(waiting_orders,["orderId"]).na.fill(value=0,subset=["quantity"]).withColumnRenamed("quantity", "waiting")


#delivered_products=products_and_orders.join(completed_orders,["orderId"]).na.fill(value=0,subset=["quantity"]).groupBy("prod").sum("quantity").withColumnRenamed("sum(quantity)", "delivered")

#waiting_products=products_and_orders.join(waiting_orders,["orderId"]).na.fill(value=0,subset=["quantity"]).groupBy("prod").sum("quantity").withColumnRenamed("sum(quantity)", "waiting")

prod=delivered_products.join(waiting_products,["prod"],"full").na.fill(value=0,subset=["delivered"]).na.fill(value=0,subset=["waiting"])

prod_data=prod.rdd.map(lambda x:(x["prod"],(x["delivered"],x["waiting"]))).reduceByKey(lambda x,y:(x[0]+y[0],x[1]+y[1]))



result=prod_data.collect()
podaci = []
for red in list(result):
    list=[]
    list.append(red[0])
    list.append(red[1][0])
    list.append(red[1][1])
    podaci.append(list)


print( "|TAMZ|" + json.dumps(podaci) + "|TAMZ|"  )


spark.stop()

