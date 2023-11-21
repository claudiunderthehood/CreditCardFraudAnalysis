#!/usr/bin/env bash
# Stop

docker stop logstash

# Remove previuos container 
docker container rm logstash

docker build ../logstash/ --tag tap:logstash 
docker run -t --name logstash --network tap -p 5044:5044 tap:logstash