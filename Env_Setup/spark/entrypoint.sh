rm -rf job-package
mkdir job_package
cp common.py job_package/common.py
zip -r -j job_zip.zip job_package/*.py
cp ./job_zip.zip <path to docker-compose folder>/apps
cp ./job.py <path to docker-compose folder>/apps
cp <path to data>/yellow_tripdata_2023-09.parquet <path to docker-spark-cluster folder>/data
