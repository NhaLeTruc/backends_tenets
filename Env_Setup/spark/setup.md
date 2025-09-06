# Setting up Spark projects

## PySpark

> Reference: [guide](https://medium.com/@suffyan.asad1/spark-essentials-a-guide-to-setting-up-packaging-and-running-pyspark-projects-2eb2a27523a3)

In local mode, all the tasks run on the driver, which has 4 cores as was configured earlier. In addition to the local mode, Spark applications can also be run on Spark clusters in Client or Cluster modes.

### Packaging and Executing on a Spark cluster

Next step is to prepare the application to execute on a Spark cluster. The following steps will be required to prepare the job and to run it on a cluster. These steps are quite generic for PySpark jobs, whether they are to be submitted to self-managed clusters, or to managed clusters on one of the public clouds such as for Amazon Elastic MapReduce (EMR). Some additional steps maybe required for public clouds which can be determined from their documentation. The steps are:

+ Update the code that creates Spark Session to exclude local as master.
+ Prepare two artifacts: the Python file containing the main function and the driver code that acts as the entry-point of the job, and a package (.zip in this case) containing other Python files.
+ Submit the job to the test cluster using the spark-submit command.

> NOTE: A note about the first point (updating the creation of Spark Session): In real projects, the best practice is to write unit-tests to test the code, and in that case, a local session should be created to run the unit-tests, whereas the main code should only create Spark Session for the environment the job is destined for.

+ For jobs submitted to short-lived (ephemeral) clusters that are spun up on for particular jobs or sets of related jobs, it is usually appropriate to install the required libraries when spinning up the cluster. Spark distributions provided by public clouds mostly provide a mechanism to run scripts, that can, in addition to other things, install the required packages. An example of such mechanism is Bootstrap Actions in Amazon Elastic MapReduce (EMR). This is becoming a common mechanism due to the popularity of ephemeral clusters on public clouds due to cost-effectiveness, and long-running clusters are only spun up for streaming use-cases or if absolutely necessary.
+ In a shared cluster environment, directly installing dependencies on nodes might not be feasible due to potential conflicts with the dependencies of other jobs. In such cases, **bundling dependencies** with each job ensures they are accessible when needed.

If required external packages are needed to be submitted with the job, zipping is not ideal, as packaging in a .zip file does not support including packages built as Wheel. The other packaging options available are:

+ Packaging using Conda (conda-pack)
+ Packaging using Virtualenv
+ Packaging using PEX

[Python package management doc](https://spark.apache.org/docs/latest/api/python/tutorial/python_packaging.html)

### Setting up a locally running cluster for testing

Docker Spark cluster setup using docker compose for local testing is ideal.

> NOTE: keep two mounts for code and data on Spark master docker.
> For example: `/opt/spark-apps` and `/opt/spark-data`.

### Preparing, packaging, and executing the job on the test cluster

Use `entrypoint.sh` to zip then mount code and data onto test docker Spark cluster. After which these command would run `spark-submit`:

```bash
rm -rf job-package
mkdir job_package
cp common.py job_package/common.py
zip -r -j job_zip.zip job_package/*.py
cp ./job_zip.zip <path to docker-compose folder>/apps
cp ./job.py <path to docker-compose folder>/apps
cp <path to data>/yellow_tripdata_2023-09.parquet <path to docker-spark-cluster folder>/data

docker exec -it docker-spark-cluster-spark-master-1 /bin/bash

/opt/spark/bin/spark-submit --master <master URL> --py-files /opt/spark-apps/job_zip.zip /opt/spark-apps/job.py

```

> Remember to update the <master URL> placeholder in the command with the URL of Spark master on your system. It can be determined by visiting localhost:9000 on the browser to view the Spark environment details.
-------------
> The spark master URL might change if the docker-compose cluster is stopped and restarted, so in that case, make sure to get the latest Spark URL.

### Packaging a job with dependent libraries

In addition to Python files, your PySpark job may require additional Python packages not present on the Spark cluster. Let’s enhance the previous job example by incorporating packages like Pandas, Numpy, and Apache Arrow and examine how to package these dependencies with the PySpark job. These packages are not present on the Spark cluster used for testing.

The job now uses Pandas UDF, which require PyArrow and Pandas libraries, so requirements.txt will be updated. And Spark session creation code also needs to be updated to enable Pandas UDFs.

Next step is to prepare the job for execution on the test cluster. This job, in addition to two python files — analysis.py and common.py, requires Numpy, Pandas, and Apache Arrow as dependencies. These dependencies are not present on the Spark cluster, and they have to be submitted with the Spark job. If only the code is packaged and submitted, the job fails with package not found exceptions. For this demonstration, the following items are created in the packaging process of the job:

+ second_job.py file: The main file of the second analysis job.
+ analysis_job.zip package: This ZIP package contains the common.py and analysis.py files. Its preparation is done using the same method as demonstrated in the prior example. These are provided to the cluster by using the —py-files argument.
+ job_dependencies.tar.gz package: The package containing the dependent libraries, and also contains Python from the virtual environment. The compilation of this package will be done using the venv-pack Python package, which packs the current state of the virtual environment i.e. packages all the libraries installed in the virtual environment. The package is then copied to the cluster, and is passed to the executors using the --archives flag. For providing the dependencies to the driver, and for making Spark use Python from the package, it needs to be unpacked on the master node. To ensure that Spark uses Python in the package, the PYSPARK_PYTHON flag needs to be set to Python in the package folder that has just been unpacked.

> The job_dependencies.tar.gz package needs to be prepared on a system that is running the same Operating System as the one running on the Spark cluster’s master node, and should be as close to it as possible. Ideally, this can be done by compiling the package on the master node itself, but depending on access policies of organizations, it may not be possible.

Additionally, create a folder called package_env in the project folder. This will be mounted as volume to the docker container to put the requirements.txt file in the container, and to retrieve the package. The following commands will do it:

```bash
mkdir package_env
cp requirements.txt package_env.requirements.txt

docker build -t build-image:latest ./build_image
docker run -v ${PWD}/package_env:/project_files -it build-image:latest /bin/bash

python3 -m venv --copies venv
source venv/bin/activate
pip3 install -r requirements.txt
pip3 install venv-pack
venv-pack -o job_dependencies.tar.gz
```

After executing the commands, the package is created in the package_env folder. This package needs to be copied to the Spark cluster, to the same shared folder that was used earlier in the first example. But before that, lets create another package containing common.py and analysis.py files. Run the following commands on the terminal after exiting from the docker container. Use the exit command to exit the interactive mode and to shut-down the container.

```bash
mkdir analysis_job_package
cp common.py ./analysis_job_package/common.py
cp analysis.py ./analysis_job_package/analysis.py
cd analysis_job_package
zip -r ../analysis_job_zip.zip .
cd ..
```

Finally, the 3 items need to be copied to the Spark cluster, to the apps folder in the docker-spark-cluster folder that has been mounted as a volume on the Spark master node. Run the following commands:

```bash
cp second_job.py <path to docker-spark-cluster>/apps/second_job.py
cp analysis_job_zip.zip <path to docker-spark-cluster>/apps/analysis_job_zip.zip
cp package_env/job_dependencies.tar.gz <path to docker-spark-cluster>/apps/job_dependencies.tar.gz
```

Next steps are:

+ Connect to the Spark master node in interactive mode
+ Create a folder called environment
+ Unpack the job_dependencies.tar.gz to the environment folder
+ Point Spark to use Python in the environment folder
+ Execute the job

```bash
docker exec -it docker-spark-cluster-spark-master-1 /bin/bash
mkdir environment
tar -xzf /opt/spark-apps/job_dependencies.tar.gz -C ./environment
export PYSPARK_PYTHON=./environment/bin/python
/opt/spark/bin/spark-submit --master <spark master URL> --archives /opt/spark-apps/job_dependencies.tar.gz#environment --py-files /opt/spark-apps/analysis_job_zip.zip /opt/spark-apps/second_job.py
```

> The job appears in the Spark UI at http://localhost:9000, and job progress can be tracked in the Spark UI at http://localhost:4040.
-------------
> In real projects, the process of packaging and deployment of the job to the cluster is managed by a CI/CD pipeline, and the job is usually scheduled and executed using an orchestrator such as Apache Airflow as part of a bigger pipeline. The above examples have been written for beginners, and should provide a good reference of the overall process, however, the steps may vary slightly depending on the project, the nature of the target Spark cluster, tech stack, and many other things.
