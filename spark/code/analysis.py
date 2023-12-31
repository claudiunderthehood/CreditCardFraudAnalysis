from __future__ import print_function

from pyspark import SparkContext
from pyspark.sql.session import SparkSession
from pyspark.conf import SparkConf
from pyspark import SparkContext
from pyspark.sql.session import SparkSession
from pyspark.sql.functions import *
import pyspark.sql.types as tp
from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import LogisticRegression
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame

sc = SparkContext(appName="transactionsAnalysis")
spark = SparkSession(sc)
sc.setLogLevel("WARN")


file="/opt/tap/spark/dataset/transactions.csv"
print("-------------- \n Start:\n")

schema= tp.StructType([
    tp.StructField(name= 'TRANSACTION_ID', dataType= tp.IntegerType(),  nullable= True),
    tp.StructField(name= 'TX_DATETIME', dataType= tp.TimestampType(),  nullable= True),
    tp.StructField(name= 'CUSTOMER_ID', dataType= tp.IntegerType(),  nullable= True),
    tp.StructField(name= 'TERMINAL_ID', dataType= tp.IntegerType(),  nullable= True),
    tp.StructField(name= 'TX_AMOUNT', dataType= tp.DoubleType(),  nullable= True),
    tp.StructField(name= 'TX_TIME_SECONDS', dataType= tp.IntegerType(),  nullable= True),
    tp.StructField(name= 'TX_TIME_DAYS', dataType= tp.IntegerType(),  nullable= True),
    tp.StructField(name= 'TX_FRAUD', dataType= tp.DoubleType(),  nullable= True),
    tp.StructField(name= 'TX_FRAUD_SCENARIO', dataType= tp.IntegerType(),  nullable= True),
    tp.StructField(name= 'TX_DURING_WEEKEND', dataType= tp.IntegerType(),  nullable= True),
    tp.StructField(name= 'TX_DURING_NIGHT', dataType= tp.IntegerType(),  nullable= True),
])

train_set = spark.read.csv(file, header=True, schema=schema, sep=",")

train_set = train_set.drop("TX_TIME_DAYS")
train_set = train_set.drop("TX_FRAUD_SCENARIO")

input_features=['TX_AMOUNT','TX_FRAUD']

assembler = VectorAssembler(inputCols=input_features, outputCol='features')

regression= LogisticRegression(featuresCol= 'features', labelCol='TX_FRAUD')
pipeline=Pipeline(stages=[assembler, regression])
pipelineFit= pipeline.fit(train_set)
updated_train_set = pipelineFit.transform(train_set)
updated_train_set.show()

print("------------------- \n PipelineFit\n")

elastic_host="10.0.100.51"
elastic_index="transactions"
elastic_document="_doc"

es_mapping = {
    "mappings": {
        "properties":
            {
                "id" : {"type": "integer","fielddata": True},
                "@timestamp": {"type": "date","format": "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'"}
            }
    }
}

def get_spark_session():
    sparkConf= SparkConf() \
                .set("es.nodes", elastic_host) \
                .set("es.port", "9200") \
                .set("spark.app.name", "transactionsAnalysis") \
                .set("spark.scheduler.mode", "FAIR")
    sc = SparkContext.getOrCreate(conf=sparkConf)


print("--------------------- \n Es setup\n")


kafkaServer="10.0.100.23:9092"
topic = "transactions"

conf = SparkConf(loadDefaults=False)

dataKafka = tp.StructType([
    tp.StructField(name= 'TRANSACTION_ID', dataType= tp.IntegerType(),  nullable= True),
    tp.StructField(name= 'TX_DATETIME', dataType= tp.LongType(),  nullable= True),
    tp.StructField(name= 'CUSTOMER_ID', dataType= tp.IntegerType(),  nullable= True),
    tp.StructField(name= 'TERMINAL_ID', dataType= tp.IntegerType(),  nullable= True),
    tp.StructField(name= 'TX_AMOUNT', dataType= tp.DoubleType(),  nullable= True),
    tp.StructField(name= 'TX_TIME_SECONDS', dataType= tp.IntegerType(),  nullable= True),
    tp.StructField(name= 'TX_FRAUD', dataType= tp.DoubleType(),  nullable= True),
    tp.StructField(name= 'TX_DURING_NIGHT', dataType= tp.IntegerType(),  nullable= True),
    tp.StructField(name= '@timestamp', dataType= tp.TimestampType(),  nullable= True)
])

def process(batch_df: DataFrame, batch_id: int):

    if not batch_df.rdd.isEmpty():
        print("----------------- \n Processing\n")
        batch_df.show()

        batch_df = batch_df.withColumn('TX_DATETIME', from_unixtime(col('TX_DATETIME') / 1000))
        data2=pipelineFit.transform(batch_df)
        data2.summary()
        data2.show()

        print("--------------------- \nSending data to ES \n")
        data2.select("TRANSACTION_ID", "TX_DATETIME", "CUSTOMER_ID", "TERMINAL_ID", "TX_AMOUNT",
                     "TX_TIME_SECONDS", "TX_DURING_NIGHT", "@timestamp", "prediction") \
        .write \
        .format("org.elasticsearch.spark.sql") \
        .mode('append') \
        .option("es.mapping.id","TRANSACTION_ID") \
        .option("es.nodes", elastic_host).save(elastic_index)



print("----------------------- \n Creating a kafka source\n")

df = spark \
  .readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", kafkaServer) \
  .option("subscribe", topic) \
  .load()


print("------------------------ \nTaking data from kafka\n")


df.selectExpr("CAST(value AS STRING)") \
    .select(from_json("value", dataKafka).alias("data")) \
    .select("data.*") \
    .writeStream \
    .foreachBatch(process) \
    .start() \
    .awaitTermination()


print("---------------------- \n kafka server\n")