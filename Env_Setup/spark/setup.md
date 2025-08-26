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
docker exec -it docker-spark-cluster-spark-master-1 /bin/bash

/opt/spark/bin/spark-submit --master <master URL> --py-files /opt/spark-apps/job_zip.zip /opt/spark-apps/job.py

```

> Remember to update the <master URL> placeholder in the command with the URL of Spark master on your system. It can be determined by visiting localhost:9000 on the browser to view the Spark environment details.
-------------
> The spark master URL might change if the docker-compose cluster is stopped and restarted, so in that case, make sure to get the latest Spark URL.


