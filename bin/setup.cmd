REM Stop
docker stop kafkaZK kafkaServer spark generator logstash elasticsearch kibana 

REM Remove Containers
docker rm kafkaZK kafkaServer spark generator logstash elasticsearch kibana 

REM Remove images
docker rmi tap:kafka tap:elasticsearch tap:kibana tap:spark tap:logstash tap:generator

REM Build images
docker build ../elasticsearch/ --tag tap:elasticsearch

docker build ../transactions_generator/ --tag tap:generator

docker build ../kafka/ --tag tap:kafka

docker build ../kibana/ --tag tap:kibana

docker build ../spark/ --tag tap:spark

docker build ../logstash/ --tag tap:logstash
