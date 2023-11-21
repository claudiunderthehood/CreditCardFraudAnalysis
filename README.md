# Credit card fraud analysis

This project is meant to analyse in real time, every day transactions in order to detect frauds within transactions through linear regression. The whole data is processed through a pipeline which features: Logstash, Kafka, 
Spark, Elasticsearch and Kibana.

## Requirements

Docker is crucial for this pipeline, so make sure to install it before running everything. You'll need to install [spark](https://archive.apache.org/dist/spark/spark-3.1.1/pyspark-3.1.1.tar.gz) and place the .tar file in the "spark/setup/" directory.

## Usage

In order to run the pipeline, start docker. Then open 7 terminals and go to the "bin/" directory. In here you'll need to run:

```bash
./tapInit.sh

./kafkaStartZK.sh

./kafkaStartServer.sh

./elasticsearch.sh

./kibana.sh

./sparkSubmitPython.sh analysis.py "org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.1,org.elasticsearch:elasticsearch-spark-30_2.12:7.12.1"

./logstash.sh

./generator.sh
```

Execute them in this order and have fun with kibana(http://localhost:5601) :)

