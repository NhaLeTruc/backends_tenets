# A typical Makefile for docker env operations

```Makefile
# Docker Compose wrapper
DC = docker compose

.PHONY: up down deep_down deep_clean pg_dvd apps_zip spark_submit test_pipelines code_quality

up:
	sudo $(DC) up -d

down:
	sudo $(DC) down

deep_down:
	sudo $(DC) down --volumes --remove-orphans
	sudo docker network prune -f
	sudo docker builder prune -fa

pg_dvd:
	sudo docker cp apps/test/data/dvdrental.zip postgres-metadata:/
	sudo docker exec postgres-metadata bash -c "apt update; apt install pv unzip; unzip dvdrental.zip; pv dvdrental.tar | pg_restore -U postgres_usr -d dvdrental"

apps_zip:
	zip -r apps.zip apps/
	mv apps.zip spark/apps/
	cp apps/pipelines/main.py spark/apps/

spark_submit:
	sudo docker exec -w /opt/bitnami/spark/apps spark-master spark-submit \
		--master spark://spark-master:7077 \
		--deploy-mode client \
		--py-files apps.zip \
		main.py

test_pipelines:
	make apps_zip
	make spark_submit

code_quality:
	ruff check --fix apps
	mypy --pretty apps --explicit-package-bases
```
