#!/bin/bash

# Run the PySpark script and redirect the output to a file
spark-submit --master local spark_products.py > output.txt

# Read the output file and return the content
cat output.txt