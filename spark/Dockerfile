FROM openjdk:8-jre

ENV PATH $SPARK_DIR/bin:$PATH
ENV SPARK_VERSION=3.1.1
ENV SPARK_DIR=/opt/spark
ENV PATH $SPARK_DIR/bin:$PATH

ADD setup/spark-${SPARK_VERSION}-bin-hadoop2.7.tar /opt

RUN apt-get update && apt-get -y install bash python3 python3-pip netcat

RUN pip3 install pyspark numpy elasticsearch
# Create Sym Link 
RUN ln -s /opt/spark-${SPARK_VERSION}-bin-hadoop2.7 ${SPARK_DIR}

ADD dataset /opt/tap/spark/dataset
# Add Python Code
ADD code/*  /opt/tap/

# Add Spark Manager
ADD spark-manager.sh $SPARK_DIR/bin/spark-manager

RUN chmod +x ${SPARK_DIR}/bin/spark-manager


WORKDIR ${SPARK_DIR}
ENTRYPOINT [ "spark-manager" ]