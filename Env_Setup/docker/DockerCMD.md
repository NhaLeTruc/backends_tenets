# Useful docker commands

```bash
sudo docker compose up -d

sudo watch docker ps -a

sudo watch docker images -a

sudo docker stop $(sudo docker ps -qa)

sudo docker start $(sudo docker ps -qa)

sudo docker rmi -f $(sudo docker images --filter=reference='data_quality_in_*' -qa)

sudo docker images --format "{{.ID}}\t{{.Size}}\t{{.Repository}}:{{.Tag}}" | sort -k 2 -h

sudo docker exec -it <CONTAINER_ID> bash

sudo docker inspect <CONTAINER_ID> | grep "IPAddress"

sudo docker compose up --build --no-deps --force-recreate

sudo docker compose down --volumes --remove-orphans

sudo docker compose down -rmi all

sudo docker network prune --force

sudo docker volume ls

sudo docker logs <CONTAINER_ID>

# Show Jupyter's kernels
jupyter kernelspec list

# Show OS info
cat /etc/os-release

# Load postgres example database dvdrental at https://neon.com/postgresql/postgresql-getting-started/postgresql-sample-database
sudo docker cp apps/test/data/dvdrental.zip postgres-metadata:/

sudo docker exec postgres-metadata bash -c "apt update; apt install pv unzip; unzip dvdrental.zip; pv dvdrental.tar | pg_restore -U postgres_usr -d dvdrental"

psql -U postgres_usr -d dvdrental

# Move file from container to local
sudo docker cp <CONTAINER_ID>:</path/to/file/file.ext> </path/on/local/>

# Find Minio endpoint from spark master
curl -v minio-lake:9000 2>&1 | grep -o -m 1 "(.*)." | tr -d '() '

# Livy API
curl -X POST -H "Content-Type: application/json" -d '{"kind": "spark"}' http://localhost:8998/sessions
curl -X GET http://localhost:8998/sessions/{sessionId}
curl -X POST -H "Content-Type: application/json" -d '{"code": "1 + 1"}' http://localhost:8998/sessions/{sessionId}/statements
curl -X POST -H "Content-Type: application/json" -d '{"file": "/path/to/your/spark_app.jar", "className": "com.example.MySparkApp"}' http://localhost:8998/batches

# Move file from container to local
sudo docker cp <CONTAINER_ID>:</path/to/file/file.ext> </path/on/local/>

# List branches
curl -X GET http://192.168.1.111:19120/api/v2/trees

# List namespaces in branch main
curl -X GET http://192.168.1.111:19120/api/v1/namespaces/main

# List log of branch main
curl -X GET http://192.168.1.111:19120/api/v1/trees/tree/main/log

curl -X GET http://192.168.1.111:19120/api/v2/trees/main/recent-changes

curl -X GET http://192.168.1.111:19120/api/v2/trees/main/history

# List namespaces and their tables in branch main
curl -X GET http://192.168.1.111:19120/api/v2/trees/main/entries
# List tables in branch main - should work in linux
curl -X GET http://192.168.1.111:19120/api/v2/trees/main/entries | jq '.entries[] | select(.type == "ICEBERG_TABLE")'

# List info of namespce sales and its table sales_data_raw
curl -X GET http://192.168.1.111:19120/api/v2/trees/main/contents/sales
curl -X GET http://192.168.1.111:19120/api/v2/trees/main/contents/sales.sales_data_raw

curl -v minio-lake:9000 2>&1 | grep -o "(.*)." | tr -d '() '


```
