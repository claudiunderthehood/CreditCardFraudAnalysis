FROM docker.elastic.co/logstash/logstash:8.1.1 AS builder

RUN rm -f /usr/share/logstash/pipeline/logstash.conf
RUN rm -f /usr/share/logstash/transactions.csv
RUN rm -f /usr/share/logstash/completed.log
ADD pipeline/ /usr/share/logstash/pipeline/




