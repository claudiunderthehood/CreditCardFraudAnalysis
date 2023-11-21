docker stop generator

# Remove previuos container 
docker container rm generator

docker build ../transactions_generator/ --tag tap:generator
docker run -t --name generator --network tap tap:generator