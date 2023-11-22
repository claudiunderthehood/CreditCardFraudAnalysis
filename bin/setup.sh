#!/usr/bin/env bash

docker stop kafkaZK kafkaServer spark generator logstash elasticsearch kibana 

docker rm kafkaZK kafkaServer spark generator logstash elasticsearch kibana 

docker rmi tap:kafka tap:elasticsearch tap:kibana tap:spark tap:logstash tap:generator

docker build ../elasticsearch/ --tag tap:elasticsearch

docker build ../transactions_generator/ --tag tap:generator

docker build ../kafka/ --tag tap:kafka

docker build ../kibana/ --tag tap:kibana

docker build ../spark/ --tag tap:spark

docker build ../logstash/ --tag tap:logstash 


