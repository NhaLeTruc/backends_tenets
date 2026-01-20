# DevOps/Platform Engineer Interview Transcript

---

## Part 1: CI/CD Fundamentals for Data Engineering

**Question:** How do CI/CD principles for data engineering differ from traditional software engineering?

**Answer:** There are several key differences:

First, **data validation vs. code validation**. In traditional CI/CD, we test code logic. In data engineering, we need to validate both code AND data quality. This means schema validation, data profiling, statistical tests, and ensuring data lineage is maintained.

Second, **stateful vs. stateless**. Most applications are designed to be stateless, but data pipelines are inherently stateful. We need to handle incremental processing, checkpointing, and ensure idempotency. Our CI/CD must test state recovery scenarios.

Third, **environment parity challenges**. Production data volumes can be orders of magnitude larger than test data. We can't always replicate production conditions, so we need representative sampling strategies and volume testing approaches.

Fourth, **longer feedback loops**. A data pipeline might process terabytes and run for hours. We can't wait that long in CI, so we need strategies like subset testing, synthetic data generation, and tiered testing approaches.

Finally, **dependency complexity**. Data pipelines often depend on external data sources, databases, message queues, and data lakes. Mock strategies are harder and integration testing becomes more critical.

**Question:** How do you handle the challenge of testing with realistic data volumes in CI without waiting hours?

**Answer:** I use a multi-tiered testing strategy:

**Tier 1 - Unit Tests:** Run in seconds. Test individual transformations with minimal synthetic data. Focus on logic correctness, edge cases, and data type handling.

**Tier 2 - Integration Tests:** Run in minutes. Use stratified sampling of real production data—typically 1-5% of volume but maintaining statistical properties. Test schema evolution, data quality rules, and integration points.

**Tier 3 - Smoke Tests in Staging:** Run in 15-30 minutes. Process recent data partitions (e.g., last hour or day) through the full pipeline to validate end-to-end flow.

**Tier 4 - Canary/Shadow Tests in Production:** Run continuously. Deploy new versions alongside old ones, compare outputs, gradually shift traffic.

The key is that Tiers 1-2 run in every PR. Tier 3 runs on merge to main. Tier 4 runs during deployment. This gives fast feedback while maintaining confidence.

**Question:** Good. Now, what are the most critical quality gates you implement in a data pipeline CI/CD process?

**Answer:** I implement several mandatory gates:

1. **Schema Contract Validation:** Ensure output schema matches the contract. Breaking schema changes must be explicit and versioned.

2. **Data Quality Assertions:** Row count thresholds, null percentage checks, uniqueness constraints, referential integrity, value range validations. These use tools like Great Expectations or custom validators.

3. **Data Drift Detection:** Compare statistical properties (distributions, correlations) against baseline. Flag significant deviations.

4. **Backward Compatibility Tests:** Ensure new pipeline versions can process data from previous versions and produce compatible outputs.

5. **Performance Benchmarks:** Track processing time, memory usage, and cost. Fail if regression exceeds threshold (e.g., 20% slower).

6. **Security Scans:** Dependency vulnerability scanning, secrets detection, data access auditing.

7. **Lineage Verification:** Ensure metadata lineage is captured correctly for regulatory compliance.

Each gate failure blocks promotion to the next environment unless explicitly overridden with documented justification.

**Question:** How do you handle schema evolution in CI/CD pipelines?

**Answer:** Schema evolution requires careful orchestration:

**For backward-compatible changes** (adding optional columns, widening types):
- Automated tests verify old queries still work
- Data quality checks validate new columns with appropriate null handling
- Deploy pipeline first, then update consumers
- Use schema registries (like Confluent Schema Registry or AWS Glue Schema Registry) with compatibility modes set to BACKWARD

**For breaking changes** (removing columns, narrowing types, renaming):
- Implement a multi-phase rollout:
  - Phase 1: Dual-write period—write both old and new schemas
  - Phase 2: Migrate consumers to new schema
  - Phase 3: Deprecate old schema with monitoring
  - Phase 4: Remove old schema
- CI/CD must validate each phase independently
- Use feature flags to control rollout pace
- Maintain schema version in metadata and CI tests validate version compatibility

**Tooling:**
- Schema registry integration in CI to auto-check compatibility
- Contract testing between producer and consumer pipelines
- Automated migration script generation and testing

---

## Part 3: Jenkins Deep Dive

**Question:** Let's talk about Jenkins specifically. How would you structure a Jenkinsfile for a complex data pipeline with multiple stages?

**Answer:** I'd structure it with clear separation of concerns and parallelization:

```groovy
pipeline {
    agent none

    options {
        timeout(time: 2, unit: 'HOURS')
        buildDiscarder(logRotator(numToKeepStr: '30'))
        disableConcurrentBuilds()
        timestamps()
    }

    environment {
        PIPELINE_NAME = 'customer-analytics'
        DOCKER_REGISTRY = 'company.registry.io'
        K8S_NAMESPACE = "data-pipelines-${env.BRANCH_NAME}"
        ANSIBLE_VAULT_PASSWORD = credentials('ansible-vault-key')
    }

    stages {
        stage('Initialize') {
            agent { label 'lightweight' }
            steps {
                script {
                    env.VERSION = sh(script: "git describe --tags --always", returnStdout: true).trim()
                    env.BUILD_TIME = sh(script: "date -u +%Y%m%d-%H%M%S", returnStdout: true).trim()
                }
                checkout scm
            }
        }

        stage('Code Quality & Security') {
            parallel {
                stage('Lint') {
                    agent { docker { image 'python:3.11' } }
                    steps {
                        sh 'pip install ruff black mypy'
                        sh 'ruff check .'
                        sh 'black --check .'
                        sh 'mypy src/'
                    }
                }
                stage('Security Scan') {
                    agent { label 'security' }
                    steps {
                        sh 'bandit -r src/ -f json -o bandit-report.json'
                        sh 'safety check --json'
                        sh 'git secrets --scan'
                    }
                }
                stage('Dependency Check') {
                    agent { label 'lightweight' }
                    steps {
                        sh 'pip-audit -r requirements.txt'
                    }
                }
            }
        }

        stage('Build') {
            agent { label 'docker' }
            steps {
                script {
                    dockerImage = docker.build(
                        "${DOCKER_REGISTRY}/${PIPELINE_NAME}:${VERSION}",
                        "--build-arg BUILD_TIME=${BUILD_TIME} ."
                    )
                }
            }
        }

        stage('Test') {
            parallel {
                stage('Unit Tests') {
                    agent {
                        docker {
                            image "${DOCKER_REGISTRY}/${PIPELINE_NAME}:${VERSION}"
                            args '-v /tmp/test-data:/data'
                        }
                    }
                    steps {
                        sh 'pytest tests/unit/ -v --cov=src --cov-report=xml'
                        junit 'test-results/unit/*.xml'
                        publishCoverage adapters: [coberturaAdapter('coverage.xml')]
                    }
                }
                stage('Integration Tests') {
                    agent {
                        kubernetes {
                            yaml libraryResource('k8s-test-pod.yaml')
                        }
                    }
                    steps {
                        container('spark') {
                            sh 'pytest tests/integration/ -v --spark'
                        }
                    }
                }
                stage('Data Quality Tests') {
                    agent { label 'data-testing' }
                    steps {
                        sh 'great_expectations checkpoint run pipeline_validation'
                        publishHTML target: [
                            reportDir: 'ge-reports',
                            reportFiles: 'index.html',
                            reportName: 'Data Quality Report'
                        ]
                    }
                }
            }
        }

        stage('Schema Validation') {
            agent { label 'lightweight' }
            steps {
                sh '''
                    python scripts/validate_schema.py \
                        --registry-url ${SCHEMA_REGISTRY_URL} \
                        --compatibility BACKWARD \
                        --schema schemas/output.avsc
                '''
            }
        }

        stage('Performance Benchmark') {
            agent { label 'performance' }
            when { branch 'main' }
            steps {
                sh 'python scripts/benchmark.py --baseline-commit main'
                script {
                    def regression = sh(
                        script: 'cat benchmark-results.json | jq .regression',
                        returnStdout: true
                    ).trim()
                    if (regression.toFloat() > 20.0) {
                        error("Performance regression exceeds 20%: ${regression}%")
                    }
                }
            }
        }

        stage('Push Image') {
            agent { label 'docker' }
            when { branch 'main' }
            steps {
                script {
                    docker.withRegistry("https://${DOCKER_REGISTRY}", 'registry-credentials') {
                        dockerImage.push("${VERSION}")
                        dockerImage.push("latest")
                    }
                }
            }
        }

        stage('Deploy to Staging') {
            agent { label 'ansible' }
            when { branch 'main' }
            steps {
                sh '''
                    ansible-playbook \
                        -i inventory/staging \
                        --vault-password-file ${ANSIBLE_VAULT_PASSWORD} \
                        playbooks/deploy-pipeline.yml \
                        -e pipeline_version=${VERSION} \
                        -e environment=staging
                '''
                sh 'kubectl apply -f k8s/staging/ --namespace=${K8S_NAMESPACE}'
            }
        }

        stage('Smoke Test Staging') {
            agent { label 'lightweight' }
            when { branch 'main' }
            steps {
                sleep 60 // Wait for deployment
                sh 'python scripts/smoke_test.py --environment=staging'
            }
        }

        stage('Deploy to Production') {
            agent { label 'ansible' }
            when {
                branch 'main'
                beforeInput true
            }
            input {
                message "Deploy to production?"
                ok "Deploy"
                parameters {
                    choice(
                        name: 'DEPLOYMENT_STRATEGY',
                        choices: ['blue-green', 'canary', 'rolling'],
                        description: 'Deployment strategy'
                    )
                }
            }
            steps {
                sh '''
                    ansible-playbook \
                        -i inventory/production \
                        --vault-password-file ${ANSIBLE_VAULT_PASSWORD} \
                        playbooks/deploy-pipeline.yml \
                        -e pipeline_version=${VERSION} \
                        -e environment=production \
                        -e strategy=${DEPLOYMENT_STRATEGY}
                '''
            }
        }
    }

    post {
        always {
            node('lightweight') {
                cleanWs()
            }
        }
        success {
            slackSend(
                color: 'good',
                message: "Pipeline ${PIPELINE_NAME} ${VERSION} deployed successfully"
            )
        }
        failure {
            slackSend(
                color: 'danger',
                message: "Pipeline ${PIPELINE_NAME} ${VERSION} failed: ${env.BUILD_URL}"
            )
        }
    }
}
```

Key patterns here:
- **Agent none** at top level with specific agents per stage for resource optimization
- **Parallel execution** where possible
- **Timeouts** to prevent hung builds
- **Credential management** via Jenkins credentials
- **Versioning** from git tags
- **Quality gates** at each stage
- **Manual approval** for production
- **Deployment strategies** as parameters

**Question:** Good structure. How do you handle Jenkins shared libraries for data pipeline patterns?

**Answer:** Shared libraries are crucial for standardization. I structure them like this:

```
shared-library/
├── vars/
│   ├── dataValidation.groovy
│   ├── sparkSubmit.groovy
│   ├── schemaRegistry.groovy
│   └── dataQualityCheck.groovy
├── src/
│   └── com/company/pipeline/
│       ├── DataPipelineConfig.groovy
│       ├── SchemaValidator.groovy
│       └── MetricsCollector.groovy
└── resources/
    ├── k8s-spark-pod.yaml
    └── ge-checkpoint-template.yml
```

Example usage in a Jenkinsfile:

```groovy
@Library('data-pipeline-library@v2') _

pipeline {
    agent any
    stages {
        stage('Validate Schema') {
            steps {
                script {
                    schemaRegistry.validate(
                        schema: 'schemas/output.avsc',
                        compatibility: 'BACKWARD',
                        subject: 'customer-events'
                    )
                }
            }
        }
        stage('Run Spark Job') {
            steps {
                script {
                    sparkSubmit(
                        mainClass: 'com.company.CustomerAggregation',
                        sparkConf: [
                            'spark.executor.memory': '4g',
                            'spark.executor.cores': '2'
                        ],
                        args: ['--input', 's3://bucket/input', '--output', 's3://bucket/output']
                    )
                }
            }
        }
        stage('Data Quality') {
            steps {
                dataQualityCheck(
                    expectations: 'expectations/customer_suite.json',
                    dataSource: 's3://bucket/output',
                    failOnError: true
                )
            }
        }
    }
}
```

This promotes:
- **Reusability** across 50+ data pipelines
- **Consistency** in deployment patterns
- **Maintainability** with centralized updates
- **Testing** of shared logic independently

**Question:** How do you optimize Jenkins for data engineering workloads specifically?

**Answer:** Several key optimizations:

**1. Resource Management:**
- Use **Kubernetes plugin** for dynamic agent provisioning
- Create pod templates for different workload types (lightweight, spark, gpu)
- Implement **resource quotas** per namespace
- Use **node affinity** to place data-heavy jobs on high-bandwidth nodes

**2. Caching Strategies:**
- **Docker layer caching** using BuildKit or Kaniko
- **Dependency caching** (pip cache, maven .m2) on persistent volumes
- **Data caching** for test datasets on shared PVCs
- **Workspace caching** for incremental builds

**3. Parallel Execution:**
- **Matrix builds** for multi-version testing (Python 3.9, 3.10, 3.11)
- **Parallel stages** for independent tests
- **Distributed testing** using pytest-xdist or Spark test parallelization

**4. Build Triggers:**
- **Webhook triggers** from GitHub instead of polling
- **Conditional builds** to skip CI for doc-only changes
- **Scheduled triggers** for nightly full-volume tests
- **Upstream/downstream** pipeline coordination

**5. Artifact Management:**
- **Thin builds** - don't store large datasets as artifacts
- **Reference by URL** - store test data in S3, reference in builds
- **Incremental artifacts** - only store deltas
- **Artifact cleanup** policies (7-day retention for staging artifacts)

**6. Monitoring:**
- **Prometheus metrics** export from Jenkins
- **Custom metrics** for pipeline duration, success rate
- **Cost tracking** per pipeline
- **Resource utilization** dashboards

**Example configuration:**

```groovy
// Jenkinsfile with optimizations
pipeline {
    agent {
        kubernetes {
            yaml """
apiVersion: v1
kind: Pod
spec:
  nodeSelector:
    workload-type: data-processing
    network-bandwidth: high
  containers:
  - name: spark
    image: bitnami/spark:3.5
    resources:
      requests:
        memory: "8Gi"
        cpu: "4"
      limits:
        memory: "16Gi"
        cpu: "8"
    volumeMounts:
    - name: cache
      mountPath: /cache
  volumes:
  - name: cache
    persistentVolumeClaim:
      claimName: jenkins-cache-pvc
"""
        }
    }

    options {
        skipDefaultCheckout()
        skipStagesAfterUnstable()
        parallelsAlwaysFailFast()
    }

    stages {
        stage('Checkout with Cache') {
            steps {
                script {
                    checkout([
                        $class: 'GitSCM',
                        extensions: [
                            [$class: 'CloneOption', depth: 1, shallow: true],
                            [$class: 'CheckoutOption', timeout: 10]
                        ]
                    ])
                }
            }
        }
    }
}
```

---

## Part 4: Kubernetes for Data Pipelines

**Question:** Let's shift to Kubernetes. How do you architect CI/CD for deploying data pipelines on K8s?

**Answer:** The architecture has several layers:

**1. Namespace Strategy:**
```
production/
├── data-pipelines-prod      # Production pipelines
├── data-pipelines-canary    # Canary deployments
staging/
├── data-pipelines-staging   # Staging environment
dev/
├── data-pipelines-dev       # Development
├── data-pipelines-pr-123    # Ephemeral PR environments
```

**2. Deployment Manifests:**

I use **Kustomize** for environment-specific overlays:

```
k8s/
├── base/
│   ├── kustomization.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── serviceaccount.yaml
│   ├── configmap.yaml
│   └── spark-operator.yaml
└── overlays/
    ├── dev/
    │   ├── kustomization.yaml
    │   └── patches/
    ├── staging/
    │   ├── kustomization.yaml
    │   └── patches/
    └── production/
        ├── kustomization.yaml
        └── patches/
```

**3. Spark on Kubernetes:**

For Spark jobs, I use the Spark Operator:

```yaml
apiVersion: sparkoperator.k8s.io/v1beta2
kind: SparkApplication
metadata:
  name: customer-aggregation
  namespace: data-pipelines-prod
spec:
  type: Scala
  mode: cluster
  image: company.registry.io/spark-pipeline:v1.2.3
  imagePullPolicy: IfNotPresent
  mainClass: com.company.CustomerAggregation
  mainApplicationFile: local:///opt/spark/jars/pipeline.jar
  sparkVersion: "3.5.0"

  restartPolicy:
    type: OnFailure
    onFailureRetries: 3
    onFailureRetryInterval: 10
    onSubmissionFailureRetries: 5

  driver:
    cores: 2
    memory: "4g"
    serviceAccount: spark-driver
    labels:
      version: "v1.2.3"
      pipeline: "customer-aggregation"
    volumeMounts:
      - name: spark-conf
        mountPath: /opt/spark/conf

  executor:
    cores: 4
    instances: 10
    memory: "8g"
    labels:
      version: "v1.2.3"
    volumeMounts:
      - name: spark-conf
        mountPath: /opt/spark/conf

  volumes:
    - name: spark-conf
      configMap:
        name: spark-config

  sparkConf:
    "spark.kubernetes.allocation.batch.size": "10"
    "spark.kubernetes.executor.deleteOnTermination": "true"
    "spark.sql.adaptive.enabled": "true"
    "spark.sql.adaptive.coalescePartitions.enabled": "true"

  hadoopConf:
    "fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem"
    "fs.s3a.aws.credentials.provider": "com.amazonaws.auth.WebIdentityTokenCredentialsProvider"

  monitoring:
    exposeDriverMetrics: true
    exposeExecutorMetrics: true
    prometheus:
      jmxExporterJar: "/prometheus/jmx_prometheus_javaagent-0.16.1.jar"
      port: 8090
```

**4. CI/CD Integration:**

Jenkins deploys to K8s using this pattern:

```groovy
stage('Deploy to K8s') {
    steps {
        script {
            sh """
                # Apply base configuration
                kubectl apply -k k8s/overlays/${ENVIRONMENT}

                # Update image version
                kubectl set image sparkapp/customer-aggregation \
                    spark=${DOCKER_REGISTRY}/${PIPELINE_NAME}:${VERSION} \
                    -n data-pipelines-${ENVIRONMENT}

                # Wait for rollout
                kubectl wait --for=condition=Ready sparkapp/customer-aggregation \
                    -n data-pipelines-${ENVIRONMENT} \
                    --timeout=300s

                # Verify deployment
                kubectl get sparkapp customer-aggregation \
                    -n data-pipelines-${ENVIRONMENT} \
                    -o jsonpath='{.status.applicationState.state}'
            """
        }
    }
}
```

**Question:** How do you handle secrets management for data pipelines in Kubernetes?

**Answer:** Multi-layered approach:

**1. External Secrets Operator:**

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: pipeline-secrets
  namespace: data-pipelines-prod
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: pipeline-secrets
    creationPolicy: Owner
  data:
    - secretKey: db-password
      remoteRef:
        key: prod/data-pipeline/postgres
        property: password
    - secretKey: s3-access-key
      remoteRef:
        key: prod/data-pipeline/s3
        property: access_key
```

**2. Service Account with IRSA (IAM Roles for Service Accounts):**

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: spark-driver
  namespace: data-pipelines-prod
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789:role/spark-pipeline-role
```

**3. Sealed Secrets for GitOps:**

```bash
# Encrypt secrets for git storage
kubectl create secret generic app-config \
  --from-literal=api-key=supersecret \
  --dry-run=client -o yaml | \
  kubeseal -o yaml > sealed-secret.yaml
```

**4. Ansible Vault in CI/CD:**

```yaml
# ansible/vars/prod-secrets.yml (encrypted)
database_password: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          66386439653966653331613962633964...
```

**5. Secret Rotation:**

```groovy
// Jenkins job for secret rotation
pipeline {
    triggers {
        cron('H 2 * * 0') // Weekly rotation
    }
    stages {
        stage('Rotate Secrets') {
            steps {
                sh '''
                    aws secretsmanager rotate-secret \
                        --secret-id prod/data-pipeline/postgres \
                        --rotation-lambda-arn arn:aws:lambda:...
                '''
            }
        }
    }
}
```

**Question:** What about resource optimization for data workloads on K8s?

**Answer:** Critical for cost control:

**1. Cluster Autoscaling:**

```yaml
# Configure Cluster Autoscaler
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cluster-autoscaler
spec:
  template:
    spec:
      containers:
      - name: cluster-autoscaler
        image: k8s.gcr.io/autoscaling/cluster-autoscaler:v1.27.0
        command:
          - ./cluster-autoscaler
          - --cloud-provider=aws
          - --namespace=kube-system
          - --node-group-auto-discovery=asg:tag=k8s.io/cluster-autoscaler/enabled
          - --balance-similar-node-groups
          - --skip-nodes-with-system-pods=false
          - --scale-down-delay-after-add=5m
          - --scale-down-unneeded-time=10m
```

**2. Horizontal Pod Autoscaling (for streaming pipelines):**

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: kafka-consumer-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: kafka-consumer
  minReplicas: 3
  maxReplicas: 30
  metrics:
  - type: External
    external:
      metric:
        name: kafka_consumer_lag
      target:
        type: AverageValue
        averageValue: "1000"
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Pods
        value: 2
        periodSeconds: 60
```

**3. Spot Instance Strategy:**

```yaml
# Node pool for spot instances
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig
metadata:
  name: data-platform
nodeGroups:
  - name: spark-spot
    instancesDistribution:
      maxPrice: 0.50
      instanceTypes: ["r5.4xlarge", "r5a.4xlarge", "r5n.4xlarge"]
      onDemandBaseCapacity: 2
      onDemandPercentageAboveBaseCapacity: 0
      spotInstancePools: 3
    minSize: 0
    maxSize: 100
    labels:
      workload-type: data-processing
      instance-type: spot
    taints:
      - key: spot
        value: "true"
        effect: NoSchedule
```

**4. Pod Disruption Budgets:**

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: spark-executor-pdb
spec:
  minAvailable: 70%
  selector:
    matchLabels:
      spark-role: executor
```

**5. Resource Quotas per Namespace:**

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: data-pipeline-quota
  namespace: data-pipelines-prod
spec:
  hard:
    requests.cpu: "500"
    requests.memory: 2Ti
    limits.cpu: "1000"
    limits.memory: 4Ti
    persistentvolumeclaims: "50"
```

**6. Vertical Pod Autoscaling (VPA):**

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: spark-driver-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: spark-driver
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: spark
      minAllowed:
        cpu: 1
        memory: 2Gi
      maxAllowed:
        cpu: 8
        memory: 32Gi
```

---

## Part 5: Ansible for Infrastructure Automation

**Question:** Let's talk about Ansible. How do you integrate Ansible into your CI/CD pipeline for data engineering infrastructure?

**Answer:** Ansible handles infrastructure provisioning and configuration management:

**1. Repository Structure:**

```
ansible/
├── inventory/
│   ├── production/
│   │   ├── hosts.yml
│   │   └── group_vars/
│   │       ├── all.yml
│   │       ├── spark_masters.yml
│   │       └── kafka_brokers.yml
│   └── staging/
│       └── hosts.yml
├── playbooks/
│   ├── deploy-pipeline.yml
│   ├── provision-k8s-namespace.yml
│   ├── setup-monitoring.yml
│   └── backup-metadata.yml
├── roles/
│   ├── spark-operator/
│   ├── kafka/
│   ├── airflow/
│   └── prometheus/
├── group_vars/
│   └── all/
│       ├── vars.yml
│       └── vault.yml
└── ansible.cfg
```

**2. Pipeline Deployment Playbook:**

```yaml
# playbooks/deploy-pipeline.yml
---
- name: Deploy Data Pipeline
  hosts: localhost
  connection: local
  vars:
    pipeline_version: "{{ lookup('env', 'VERSION') }}"
    environment: "{{ lookup('env', 'ENVIRONMENT') }}"

  tasks:
    - name: Validate deployment prerequisites
      block:
        - name: Check if namespace exists
          kubernetes.core.k8s_info:
            kind: Namespace
            name: "data-pipelines-{{ environment }}"
          register: namespace_check

        - name: Create namespace if missing
          kubernetes.core.k8s:
            state: present
            definition:
              apiVersion: v1
              kind: Namespace
              metadata:
                name: "data-pipelines-{{ environment }}"
                labels:
                  environment: "{{ environment }}"
          when: namespace_check.resources | length == 0

    - name: Deploy infrastructure components
      include_role:
        name: "{{ item }}"
      loop:
        - spark-operator
        - monitoring
        - logging
      vars:
        target_namespace: "data-pipelines-{{ environment }}"

    - name: Apply Kustomize configuration
      kubernetes.core.k8s:
        state: present
        src: "../k8s/overlays/{{ environment }}"
        namespace: "data-pipelines-{{ environment }}"

    - name: Deploy Spark application
      kubernetes.core.k8s:
        state: present
        definition:
          apiVersion: sparkoperator.k8s.io/v1beta2
          kind: SparkApplication
          metadata:
            name: customer-aggregation
            namespace: "data-pipelines-{{ environment }}"
          spec:
            image: "{{ docker_registry }}/{{ pipeline_name }}:{{ pipeline_version }}"
            # ... (full spec from earlier)

    - name: Wait for deployment to be ready
      kubernetes.core.k8s_info:
        kind: SparkApplication
        name: customer-aggregation
        namespace: "data-pipelines-{{ environment }}"
      register: spark_app
      until: spark_app.resources[0].status.applicationState.state == "COMPLETED" or
             spark_app.resources[0].status.applicationState.state == "RUNNING"
      retries: 30
      delay: 10

    - name: Update service mesh configuration
      include_tasks: update-service-mesh.yml
      when: environment == 'production'

    - name: Register deployment in metadata store
      uri:
        url: "{{ metadata_api }}/deployments"
        method: POST
        body_format: json
        body:
          pipeline: "{{ pipeline_name }}"
          version: "{{ pipeline_version }}"
          environment: "{{ environment }}"
          timestamp: "{{ ansible_date_time.iso8601 }}"
          deployed_by: "{{ lookup('env', 'USER') }}"
        status_code: [200, 201]

    - name: Send deployment notification
      community.general.slack:
        token: "{{ slack_token }}"
        msg: "Pipeline {{ pipeline_name }} {{ pipeline_version }} deployed to {{ environment }}"
        channel: "#data-engineering"
```

**3. Dynamic Inventory from K8s:**

```python
# inventory/k8s_inventory.py
#!/usr/bin/env python3
import json
from kubernetes import client, config

def get_inventory():
    config.load_kube_config()
    v1 = client.CoreV1Api()

    inventory = {
        '_meta': {'hostvars': {}},
        'spark_executors': {'hosts': []},
        'kafka_brokers': {'hosts': []},
    }

    pods = v1.list_pod_for_all_namespaces(
        label_selector="app.kubernetes.io/component=spark-executor"
    )

    for pod in pods.items:
        pod_name = pod.metadata.name
        inventory['spark_executors']['hosts'].append(pod_name)
        inventory['_meta']['hostvars'][pod_name] = {
            'ansible_host': pod.status.pod_ip,
            'namespace': pod.metadata.namespace,
        }

    return inventory

if __name__ == '__main__':
    print(json.dumps(get_inventory(), indent=2))
```

**4. Role for Spark Operator:**

```yaml
# roles/spark-operator/tasks/main.yml
---
- name: Add Spark Operator Helm repository
  kubernetes.core.helm_repository:
    name: spark-operator
    repo_url: https://googlecloudplatform.github.io/spark-on-k8s-operator

- name: Deploy Spark Operator
  kubernetes.core.helm:
    name: spark-operator
    chart_ref: spark-operator/spark-operator
    release_namespace: spark-operator
    create_namespace: true
    values:
      sparkJobNamespace: "{{ target_namespace }}"
      webhook:
        enable: true
      metrics:
        enable: true
        port: 10254
      resources:
        limits:
          cpu: 1000m
          memory: 1Gi
        requests:
          cpu: 100m
          memory: 256Mi

- name: Create ServiceMonitor for Prometheus
  kubernetes.core.k8s:
    state: present
    definition:
      apiVersion: monitoring.coreos.com/v1
      kind: ServiceMonitor
      metadata:
        name: spark-operator
        namespace: spark-operator
      spec:
        selector:
          matchLabels:
            app: spark-operator
        endpoints:
          - port: metrics
            interval: 30s
```

**Question:** How do you handle configuration drift detection with Ansible?

**Answer:** Several strategies:

**1. Ansible Tower/AWX with Scheduled Checks:**

```yaml
# playbooks/drift-detection.yml
---
- name: Detect Configuration Drift
  hosts: all
  gather_facts: yes
  check_mode: yes
  diff_mode: yes

  tasks:
    - name: Run configuration playbooks in check mode
      include_role:
        name: "{{ item }}"
      loop:
        - spark-operator
        - monitoring
        - security-policies
      register: drift_check

    - name: Report drift if detected
      uri:
        url: "{{ monitoring_webhook }}"
        method: POST
        body_format: json
        body:
          alert: "Configuration drift detected"
          host: "{{ inventory_hostname }}"
          changes: "{{ drift_check.results }}"
      when: drift_check.changed
```

**2. GitOps Validation:**

```yaml
# Validate deployed config matches git
- name: Compare deployed vs git configuration
  block:
    - name: Get current K8s config
      kubernetes.core.k8s_info:
        kind: SparkApplication
        namespace: "{{ namespace }}"
      register: current_config

    - name: Load expected config from git
      set_fact:
        expected_config: "{{ lookup('file', 'k8s/prod/spark-app.yml') | from_yaml }}"

    - name: Detect drift
      set_fact:
        config_drift: "{{ current_config.resources[0].spec != expected_config.spec }}"

    - name: Alert on drift
      fail:
        msg: "Configuration drift detected!"
      when: config_drift and enforce_compliance
```

**3. Integration with CI/CD:**

```groovy
// Jenkins drift detection job
pipeline {
    triggers {
        cron('H */4 * * *') // Every 4 hours
    }
    stages {
        stage('Drift Detection') {
            steps {
                ansiblePlaybook(
                    playbook: 'playbooks/drift-detection.yml',
                    inventory: 'inventory/production',
                    extras: '--check --diff',
                    colorized: true
                )
            }
        }
        stage('Auto-Remediate') {
            when {
                expression {
                    return currentBuild.result == 'UNSTABLE'
                }
            }
            input {
                message "Configuration drift detected. Remediate?"
                ok "Yes"
            }
            steps {
                ansiblePlaybook(
                    playbook: 'playbooks/deploy-pipeline.yml',
                    inventory: 'inventory/production'
                )
            }
        }
    }
}
```

---

## Part 6: Advanced CI/CD Patterns

**Question:** Let's discuss some advanced patterns. How do you implement blue-green deployments for data pipelines?

**Answer:** Blue-green for data pipelines is tricky because of state. Here's my approach:

**1. Dual-Write Pattern:**

```yaml
# Deploy green version alongside blue
apiVersion: sparkoperator.k8s.io/v1beta2
kind: SparkApplication
metadata:
  name: customer-aggregation-green
  labels:
    version: green
    deployment: customer-aggregation
spec:
  # ... same spec as blue
  arguments:
    - "--output-path=s3://bucket/output-green"
    - "--checkpoint-location=s3://bucket/checkpoints-green"
---
# Existing blue version
apiVersion: sparkoperator.k8s.io/v1beta2
kind: SparkApplication
metadata:
  name: customer-aggregation-blue
  labels:
    version: blue
    deployment: customer-aggregation
spec:
  arguments:
    - "--output-path=s3://bucket/output-blue"
    - "--checkpoint-location=s3://bucket/checkpoints-blue"
```

**2. Output Validation:**

```python
# scripts/validate_blue_green.py
import pandas as pd
from scipy import stats

def compare_outputs(blue_path, green_path, threshold=0.95):
    """Compare outputs from blue and green deployments"""
    blue_df = pd.read_parquet(blue_path)
    green_df = pd.read_parquet(green_path)

    # Row count comparison
    row_diff = abs(len(blue_df) - len(green_df)) / len(blue_df)
    if row_diff > 0.05:
        raise ValueError(f"Row count diff {row_diff} exceeds threshold")

    # Schema validation
    if set(blue_df.columns) != set(green_df.columns):
        raise ValueError("Schema mismatch between blue and green")

    # Statistical comparison for numeric columns
    for col in blue_df.select_dtypes(include=['number']).columns:
        ks_stat, p_value = stats.ks_2samp(blue_df[col], green_df[col])
        if p_value < 0.05:
            print(f"Warning: Distribution diff in {col}: p={p_value}")

    # Sample exact match check
    sample_size = min(1000, len(blue_df))
    sample_match = (blue_df.sample(sample_size).sort_values('id').reset_index(drop=True) ==
                   green_df.sample(sample_size).sort_values('id').reset_index(drop=True)).all().all()

    return {
        'row_diff': row_diff,
        'schema_match': True,
        'sample_match': sample_match,
        'validation': 'PASS'
    }
```

**3. Traffic Switching:**

```yaml
# Service configuration for routing
apiVersion: v1
kind: Service
metadata:
  name: customer-aggregation-output
spec:
  selector:
    deployment: customer-aggregation
    version: blue  # Switch to 'green' after validation
  ports:
    - port: 80
      targetPort: 8080
```

**4. Orchestration in Jenkins:**

```groovy
stage('Blue-Green Deployment') {
    steps {
        script {
            // Deploy green
            sh 'kubectl apply -f k8s/green-deployment.yaml'

            // Wait for completion
            sh 'kubectl wait --for=condition=Complete sparkapp/customer-aggregation-green --timeout=1h'

            // Validate outputs
            def validation = sh(
                script: 'python scripts/validate_blue_green.py',
                returnStdout: true
            )

            if (validation.contains('PASS')) {
                // Switch traffic
                sh "kubectl patch service customer-aggregation-output -p '{\"spec\":{\"selector\":{\"version\":\"green\"}}}'"

                // Monitor for 30 minutes
                sleep 1800

                // Check metrics
                def error_rate = sh(
                    script: 'python scripts/check_metrics.py --version green',
                    returnStdout: true
                ).trim().toFloat()

                if (error_rate < 0.01) {
                    // Decommission blue
                    sh 'kubectl delete sparkapp customer-aggregation-blue'

                    // Rename green to blue for next deployment
                    sh '''
                        kubectl get sparkapp customer-aggregation-green -o yaml | \
                        sed 's/green/blue/g' | \
                        kubectl apply -f -
                    '''
                } else {
                    error "Error rate too high: ${error_rate}"
                }
            } else {
                error "Validation failed"
            }
        }
    }
}
```

**Question:** What about canary deployments?

**Answer:** Canary is better for gradual rollout:

**1. Canary with Traffic Splitting:**

```yaml
# Using Istio for traffic management
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: customer-aggregation
spec:
  hosts:
    - customer-aggregation
  http:
    - match:
        - headers:
            x-canary:
              exact: "true"
      route:
        - destination:
            host: customer-aggregation
            subset: canary
    - route:
        - destination:
            host: customer-aggregation
            subset: stable
          weight: 90
        - destination:
            host: customer-aggregation
            subset: canary
          weight: 10
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: customer-aggregation
spec:
  host: customer-aggregation
  subsets:
    - name: stable
      labels:
        version: v1.2.3
    - name: canary
      labels:
        version: v1.2.4
```

**2. Progressive Delivery:**

```groovy
stage('Canary Deployment') {
    steps {
        script {
            def weights = [5, 10, 25, 50, 100]

            for (weight in weights) {
                echo "Deploying canary at ${weight}% traffic"

                // Update traffic split
                sh """
                    kubectl patch virtualservice customer-aggregation -p '{
                        "spec": {
                            "http": [{
                                "route": [
                                    {"destination": {"subset": "stable"}, "weight": ${100 - weight}},
                                    {"destination": {"subset": "canary"}, "weight": ${weight}}
                                ]
                            }]
                        }
                    }'
                """

                // Monitor for 15 minutes
                sleep 900

                // Check metrics
                def metrics = sh(
                    script: """
                        python scripts/compare_metrics.py \
                            --stable-version v1.2.3 \
                            --canary-version v1.2.4 \
                            --duration 15m
                    """,
                    returnStdout: true
                ).trim()

                def metrics_json = readJSON text: metrics

                if (metrics_json.error_rate_diff > 0.05 || metrics_json.latency_diff > 0.20) {
                    echo "Canary metrics degraded. Rolling back."
                    sh """
                        kubectl patch virtualservice customer-aggregation -p '{
                            "spec": {
                                "http": [{
                                    "route": [
                                        {"destination": {"subset": "stable"}, "weight": 100}
                                    ]
                                }]
                            }
                        }'
                    """
                    error "Canary deployment failed"
                }
            }

            echo "Canary validated. Promoting to stable."
        }
    }
}
```

**Question:** How do you handle rollbacks in data pipelines?

**Answer:** Rollbacks are complex because of data mutations:

**1. Prevention through Immutability:**

```python
# Write data to versioned paths
output_path = f"s3://bucket/data/v{version}/date={partition_date}"
```

**2. Checkpoint Management:**

```scala
// Structured Streaming with versioned checkpoints
spark.readStream
  .format("kafka")
  .load()
  .writeStream
  .format("delta")
  .option("checkpointLocation", s"s3://bucket/checkpoints/v$version")
  .start(s"s3://bucket/output/v$version")
```

**3. Rollback Procedure:**

```groovy
stage('Rollback') {
    when {
        expression { params.ROLLBACK == true }
    }
    steps {
        script {
            def previous_version = sh(
                script: 'git describe --tags --abbrev=0 HEAD^',
                returnStdout: true
            ).trim()

            // Deploy previous version
            sh """
                kubectl set image sparkapp/customer-aggregation \
                    spark=${DOCKER_REGISTRY}/${PIPELINE_NAME}:${previous_version}
            """

            // Restore previous checkpoint
            sh """
                aws s3 sync \
                    s3://bucket/checkpoints/v${previous_version} \
                    s3://bucket/checkpoints/current \
                    --delete
            """

            // Update symbolic link for output
            sh """
                python scripts/update_output_pointer.py \
                    --version ${previous_version}
            """

            // Notify
            slackSend(
                color: 'warning',
                message: "Pipeline rolled back to ${previous_version}"
            )
        }
    }
}
```

---

## Part 7: Monitoring and Observability

**Question:** How do you implement monitoring for data pipelines in CI/CD?

**Answer:** Comprehensive monitoring across multiple layers:

**1. Pipeline Metrics:**

```python
# Instrument pipeline code
from prometheus_client import Counter, Histogram, Gauge
import time

records_processed = Counter(
    'pipeline_records_processed_total',
    'Total records processed',
    ['pipeline', 'stage']
)

processing_duration = Histogram(
    'pipeline_processing_duration_seconds',
    'Time spent processing',
    ['pipeline', 'stage']
)

current_lag = Gauge(
    'pipeline_lag_seconds',
    'Current processing lag',
    ['pipeline']
)

def process_batch(batch):
    with processing_duration.labels(
        pipeline='customer-aggregation',
        stage='transformation'
    ).time():
        result = transform(batch)
        records_processed.labels(
            pipeline='customer-aggregation',
            stage='transformation'
        ).inc(len(result))
    return result
```

**2. Data Quality Metrics:**

```yaml
# Great Expectations checkpoint with metrics
validations:
  - expectation_suite_name: customer_data_suite
    batch_request:
      datasource_name: s3_datasource
      data_asset_name: customer_events
    action_list:
      - name: store_validation_result
        action:
          class_name: StoreValidationResultAction
      - name: update_data_docs
        action:
          class_name: UpdateDataDocsAction
      - name: send_metrics_to_prometheus
        action:
          class_name: PrometheusMetricsAction
          pushgateway_url: "prometheus-pushgateway:9091"
          job_name: "data-quality-checks"
```

**3. Infrastructure Monitoring:**

```yaml
# ServiceMonitor for Spark applications
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: spark-applications
  namespace: data-pipelines-prod
spec:
  selector:
    matchLabels:
      spark-role: driver
  endpoints:
    - port: metrics
      interval: 30s
      path: /metrics
---
# PodMonitor for executors
apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata:
  name: spark-executors
  namespace: data-pipelines-prod
spec:
  selector:
    matchLabels:
      spark-role: executor
  podMetricsEndpoints:
    - port: metrics
      interval: 30s
```

**4. Alerting Rules:**

```yaml
# Prometheus alerting rules
groups:
  - name: data_pipeline_alerts
    interval: 30s
    rules:
      - alert: PipelineProcessingLag
        expr: pipeline_lag_seconds > 3600
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Pipeline {{ $labels.pipeline }} is lagging"
          description: "Processing lag is {{ $value }} seconds"

      - alert: DataQualityFailure
        expr: |
          increase(great_expectations_validation_failures_total[5m]) > 0
        labels:
          severity: critical
        annotations:
          summary: "Data quality check failed"
          description: "Expectation suite {{ $labels.suite }} failed"

      - alert: PipelineFailureRate
        expr: |
          sum(rate(pipeline_failures_total[10m])) by (pipeline) /
          sum(rate(pipeline_runs_total[10m])) by (pipeline) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High failure rate for {{ $labels.pipeline }}"
          description: "Failure rate is {{ $value | humanizePercentage }}"
```

**5. CI/CD Integration:**

```groovy
stage('Deploy Monitoring') {
    steps {
        sh '''
            # Deploy Prometheus rules
            kubectl apply -f monitoring/prometheus-rules.yaml

            # Deploy ServiceMonitors
            kubectl apply -f monitoring/service-monitors.yaml

            # Deploy Grafana dashboards
            kubectl create configmap grafana-dashboard-pipeline \
                --from-file=monitoring/dashboards/pipeline.json \
                -n monitoring \
                --dry-run=client -o yaml | kubectl apply -f -
        '''
    }
}

stage('Verify Monitoring') {
    steps {
        script {
            sleep 60 // Wait for metrics to be scraped

            def metrics_available = sh(
                script: '''
                    curl -s "http://prometheus:9090/api/v1/query?query=up{job=~\\".*customer-aggregation.*\\"}" | \
                    jq '.data.result | length'
                ''',
                returnStdout: true
            ).trim().toInteger()

            if (metrics_available == 0) {
                error "Monitoring not receiving metrics"
            }
        }
    }
}
```

**Question:** How do you implement distributed tracing for data pipelines?

**Answer:** Using OpenTelemetry:

**1. Instrumentation:**

```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Setup tracing
trace.set_tracer_provider(TracerProvider())
jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger-agent",
    agent_port=6831,
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

tracer = trace.get_tracer(__name__)

def process_pipeline(data_path):
    with tracer.start_as_current_span("pipeline_execution") as span:
        span.set_attribute("data.path", data_path)
        span.set_attribute("pipeline.version", VERSION)

        with tracer.start_as_current_span("data_ingestion"):
            data = ingest_data(data_path)
            span.set_attribute("data.records", len(data))

        with tracer.start_as_current_span("data_transformation"):
            transformed = transform_data(data)

        with tracer.start_as_current_span("data_validation"):
            validate_data(transformed)

        with tracer.start_as_current_span("data_output"):
            write_data(transformed)
```

**2. Trace Context Propagation:**

```python
# Propagate trace context through Kafka messages
from opentelemetry.propagate import inject

def send_to_kafka(message):
    headers = {}
    inject(headers)  # Inject trace context into headers

    producer.send(
        topic='customer-events',
        value=message,
        headers=list(headers.items())
    )
```

---

## Part 8: Security and Compliance

**Question:** Security is critical for data pipelines. How do you implement security controls in CI/CD?

**Answer:** Defense in depth approach:

**1. SAST/DAST in Pipeline:**

```groovy
stage('Security Scanning') {
    parallel {
        stage('SAST - Code Analysis') {
            steps {
                sh 'bandit -r src/ -f json -o bandit-report.json'
                sh 'semgrep --config=auto --json -o semgrep-report.json src/'

                // Parse and fail on high severity
                script {
                    def bandit = readJSON file: 'bandit-report.json'
                    def high_severity = bandit.results.findAll {
                        it.issue_severity == 'HIGH'
                    }
                    if (high_severity.size() > 0) {
                        error "High severity security issues found: ${high_severity.size()}"
                    }
                }
            }
        }

        stage('Dependency Scanning') {
            steps {
                sh 'pip-audit -r requirements.txt --format json -o pip-audit.json'
                sh 'safety check --json --output safety-report.json'

                // Check for critical CVEs
                script {
                    def audit = readJSON file: 'pip-audit.json'
                    def critical = audit.dependencies.findAll {
                        it.vulns.any { v -> v.severity == 'CRITICAL' }
                    }
                    if (critical.size() > 0) {
                        error "Critical vulnerabilities found"
                    }
                }
            }
        }

        stage('Container Scanning') {
            steps {
                sh """
                    trivy image \
                        --severity HIGH,CRITICAL \
                        --exit-code 1 \
                        --format json \
                        --output trivy-report.json \
                        ${DOCKER_REGISTRY}/${PIPELINE_NAME}:${VERSION}
                """
            }
        }

        stage('IaC Scanning') {
            steps {
                sh 'checkov -d k8s/ --framework kubernetes --output json > checkov-report.json'
                sh 'kube-score score k8s/*.yaml --output-format ci'
            }
        }
    }
}
```

**2. Secrets Scanning:**

```groovy
stage('Secrets Detection') {
    steps {
        sh '''
            # Scan for secrets in code
            gitleaks detect --source . --report-path gitleaks-report.json

            # Scan docker image
            docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
                aquasec/trivy image --scanners secret \
                ${DOCKER_REGISTRY}/${PIPELINE_NAME}:${VERSION}
        '''
    }
}
```

**3. Policy Enforcement with OPA:**

```yaml
# OPA policy for data pipeline deployments
package kubernetes.admission

deny[msg] {
    input.request.kind.kind == "SparkApplication"
    not input.request.object.spec.driver.serviceAccount
    msg = "SparkApplication must specify serviceAccount"
}

deny[msg] {
    input.request.kind.kind == "SparkApplication"
    input.request.object.spec.driver.resources.requests.memory
    memory_gb := to_number(replace(input.request.object.spec.driver.resources.requests.memory, "Gi", ""))
    memory_gb > 32
    msg = "Driver memory exceeds limit of 32Gi"
}

deny[msg] {
    input.request.kind.kind == "SparkApplication"
    not input.request.object.metadata.labels["data-classification"]
    msg = "SparkApplication must have data-classification label"
}
```

**4. Compliance Checks:**

```groovy
stage('Compliance Validation') {
    steps {
        script {
            // Check data retention policies
            sh '''
                python scripts/validate_retention.py \
                    --config config/retention-policy.yml \
                    --output-path s3://bucket/output
            '''

            // Verify encryption
            sh '''
                python scripts/verify_encryption.py \
                    --s3-bucket bucket \
                    --require-kms true
            '''

            // Audit data access
            sh '''
                python scripts/audit_access.py \
                    --service-account spark-driver \
                    --expected-permissions config/permissions.yml
            '''

            // PII detection
            sh '''
                python scripts/scan_pii.py \
                    --sample-data s3://bucket/output \
                    --fail-on-unencrypted true
            '''
        }
    }
}
```

**5. RBAC Enforcement:**

```yaml
# Kubernetes RBAC for pipeline
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: spark-driver-role
  namespace: data-pipelines-prod
rules:
  - apiGroups: [""]
    resources: ["pods", "services", "configmaps"]
    verbs: ["get", "list", "create", "delete"]
  - apiGroups: [""]
    resources: ["secrets"]
    verbs: ["get"]
    resourceNames: ["pipeline-secrets"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: spark-driver-binding
  namespace: data-pipelines-prod
subjects:
  - kind: ServiceAccount
    name: spark-driver
roleRef:
  kind: Role
  name: spark-driver-role
  apiGroup: rbac.authorization.k8s.io
```

---

## Part 9: Cost Optimization

**Question:** Cost is always a concern with data pipelines. What optimization techniques do you use?

**Answer:** Multiple strategies:

**1. Resource Right-Sizing:**

```python
# scripts/analyze_resource_usage.py
import boto3
from datetime import datetime, timedelta

def analyze_spark_jobs():
    """Analyze historical Spark job metrics to recommend sizing"""
    cloudwatch = boto3.client('cloudwatch')

    metrics = cloudwatch.get_metric_statistics(
        Namespace='AWS/EKS',
        MetricName='pod_memory_utilization',
        Dimensions=[
            {'Name': 'ClusterName', 'Value': 'data-platform'},
            {'Name': 'Namespace', 'Value': 'data-pipelines-prod'}
        ],
        StartTime=datetime.now() - timedelta(days=30),
        EndTime=datetime.now(),
        Period=3600,
        Statistics=['Average', 'Maximum']
    )

    avg_utilization = sum(m['Average'] for m in metrics['Datapoints']) / len(metrics['Datapoints'])
    max_utilization = max(m['Maximum'] for m in metrics['Datapoints'])

    recommendations = {
        'current_memory': '8Gi',
        'avg_utilization': f'{avg_utilization:.1f}%',
        'max_utilization': f'{max_utilization:.1f}%',
        'recommended_memory': calculate_recommendation(avg_utilization, max_utilization),
        'potential_savings': calculate_savings(avg_utilization)
    }

    return recommendations
```

**2. Auto-Scaling Configuration:**

```yaml
# Karpenter for intelligent node provisioning
apiVersion: karpenter.sh/v1alpha5
kind: Provisioner
metadata:
  name: spark-workloads
spec:
  requirements:
    - key: karpenter.sh/capacity-type
      operator: In
      values: ["spot", "on-demand"]
    - key: node.kubernetes.io/instance-type
      operator: In
      values: ["r5.4xlarge", "r5a.4xlarge", "r6i.4xlarge"]
  limits:
    resources:
      cpu: 1000
      memory: 4000Gi
  providerRef:
    name: spark-workload-template
  ttlSecondsAfterEmpty: 30
  ttlSecondsUntilExpired: 604800
  weight: 10
```

**3. Data Lifecycle Management:**

```python
# Implement tiered storage
def configure_lifecycle_policy():
    s3 = boto3.client('s3')

    lifecycle_config = {
        'Rules': [
            {
                'Id': 'MoveToIA',
                'Status': 'Enabled',
                'Transitions': [{
                    'Days': 30,
                    'StorageClass': 'STANDARD_IA'
                }],
                'Filter': {'Prefix': 'data/processed/'}
            },
            {
                'Id': 'MoveToGlacier',
                'Status': 'Enabled',
                'Transitions': [{
                    'Days': 90,
                    'StorageClass': 'GLACIER'
                }],
                'Filter': {'Prefix': 'data/archived/'}
            },
            {
                'Id': 'DeleteOldData',
                'Status': 'Enabled',
                'Expiration': {'Days': 365},
                'Filter': {'Prefix': 'data/temp/'}
            }
        ]
    }

    s3.put_bucket_lifecycle_configuration(
        Bucket='data-platform-bucket',
        LifecycleConfiguration=lifecycle_config
    )
```

**4. Query Optimization:**

```python
# Partition pruning and predicate pushdown
def optimized_read():
    df = spark.read.parquet("s3://bucket/data") \
        .filter(col("date") >= "2024-01-01") \  # Partition pruning
        .select("id", "amount", "date") \         # Column pruning
        .repartition(200, "id")                   # Optimal partitioning
    return df

# Use appropriate file formats
df.write \
    .mode("overwrite") \
    .option("compression", "snappy") \
    .partitionBy("year", "month", "day") \
    .parquet("s3://bucket/optimized-data")
```

**5. Cost Monitoring in CI/CD:**

```groovy
stage('Cost Analysis') {
    steps {
        script {
            sh '''
                python scripts/estimate_cost.py \
                    --job-name customer-aggregation \
                    --executor-count 10 \
                    --executor-memory 8g \
                    --duration-minutes 30
            '''

            def cost_estimate = readJSON file: 'cost-estimate.json'

            if (cost_estimate.estimated_cost > 100.0) {
                input message: "Estimated cost is $${cost_estimate.estimated_cost}. Proceed?",
                      ok: "Yes"
            }

            // Tag resources with cost tracking
            sh """
                kubectl label sparkapp customer-aggregation \
                    cost-center=data-engineering \
                    project=customer-analytics \
                    environment=${ENVIRONMENT}
            """
        }
    }
}
```

---

## Part 10: Testing Strategies

**Question:** Let's talk about testing. What's your testing pyramid for data pipelines?

**Answer:** The testing pyramid is inverted for data engineering:

**1. Unit Tests (30%):**

```python
# tests/unit/test_transformations.py
import pytest
from pyspark.sql import SparkSession
from src.transformations import clean_customer_data

@pytest.fixture(scope="module")
def spark():
    return SparkSession.builder \
        .appName("unit-tests") \
        .master("local[2]") \
        .getOrCreate()

def test_remove_duplicates(spark):
    input_data = [
        ("1", "John", "john@example.com"),
        ("1", "John", "john@example.com"),
        ("2", "Jane", "jane@example.com")
    ]
    df = spark.createDataFrame(input_data, ["id", "name", "email"])

    result = clean_customer_data(df)

    assert result.count() == 2
    assert result.filter(result.id == "1").count() == 1

def test_handle_null_values(spark):
    input_data = [
        ("1", None, "john@example.com"),
        ("2", "Jane", None)
    ]
    df = spark.createDataFrame(input_data, ["id", "name", "email"])

    result = clean_customer_data(df)

    # Verify nulls are handled according to business rules
    assert result.filter(result.name.isNull()).count() == 0
```

**2. Integration Tests (40%):**

```python
# tests/integration/test_pipeline.py
import pytest
from testcontainers.postgres import PostgresContainer
from testcontainers.kafka import KafkaContainer

@pytest.fixture(scope="module")
def postgres():
    with PostgresContainer("postgres:15") as postgres:
        yield postgres

@pytest.fixture(scope="module")
def kafka():
    with KafkaContainer() as kafka:
        yield kafka

def test_end_to_end_pipeline(spark, postgres, kafka):
    # Setup test data
    kafka_producer = create_producer(kafka.get_bootstrap_server())
    send_test_events(kafka_producer, count=1000)

    # Run pipeline
    from src.pipeline import run_pipeline
    run_pipeline(
        kafka_bootstrap=kafka.get_bootstrap_server(),
        db_url=postgres.get_connection_url()
    )

    # Verify results
    conn = postgres.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM customer_aggregations")
    count = cursor.fetchone()[0]

    assert count == 1000
```

**3. Data Quality Tests (20%):**

```python
# great_expectations/expectations/customer_suite.json
{
  "expectations": [
    {
      "expectation_type": "expect_table_row_count_to_be_between",
      "kwargs": {
        "min_value": 1000,
        "max_value": 1000000
      }
    },
    {
      "expectation_type": "expect_column_values_to_be_unique",
      "kwargs": {
        "column": "customer_id"
      }
    },
    {
      "expectation_type": "expect_column_values_to_not_be_null",
      "kwargs": {
        "column": "email"
      }
    },
    {
      "expectation_type": "expect_column_values_to_match_regex",
      "kwargs": {
        "column": "email",
        "regex": "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$"
      }
    },
    {
      "expectation_type": "expect_column_mean_to_be_between",
      "kwargs": {
        "column": "order_amount",
        "min_value": 10.0,
        "max_value": 1000.0
      }
    }
  ]
}
```

**4. Performance/Load Tests (10%):**

```python
# tests/performance/test_scalability.py
import pytest
from src.pipeline import run_pipeline

@pytest.mark.parametrize("data_size_gb", [1, 10, 100])
def test_pipeline_scalability(spark, data_size_gb):
    # Generate test data
    test_data = generate_synthetic_data(size_gb=data_size_gb)

    start_time = time.time()
    result = run_pipeline(test_data)
    duration = time.time() - start_time

    # Verify linear scalability
    expected_duration = data_size_gb * 60  # 1 minute per GB baseline
    assert duration < expected_duration * 1.2  # 20% tolerance

    # Verify memory usage
    max_memory = get_max_memory_usage()
    assert max_memory < data_size_gb * 2 * 1024  # 2x data size in MB
```

---

## Part 11: GitOps and Infrastructure as Code

**Question:** How do you implement GitOps for data pipelines?

**Answer:** Full GitOps with ArgoCD:

**1. Repository Structure:**

```
gitops-repo/
├── apps/
│   ├── base/
│   │   └── customer-aggregation/
│   │       ├── kustomization.yaml
│   │       └── sparkapp.yaml
│   └── overlays/
│       ├── dev/
│       ├── staging/
│       └── production/
├── infrastructure/
│   ├── spark-operator/
│   ├── monitoring/
│   └── networking/
└── argocd/
    ├── projects.yaml
    └── applications.yaml
```

**2. ArgoCD Application:**

```yaml
# argocd/applications.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: customer-aggregation-prod
  namespace: argocd
spec:
  project: data-pipelines
  source:
    repoURL: https://github.com/company/gitops-repo
    targetRevision: main
    path: apps/overlays/production/customer-aggregation
  destination:
    server: https://kubernetes.default.svc
    namespace: data-pipelines-prod
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
      allowEmpty: false
    syncOptions:
      - CreateNamespace=true
      - PruneLast=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
  ignoreDifferences:
    - group: sparkoperator.k8s.io
      kind: SparkApplication
      jsonPointers:
        - /status
```

**3. CI/CD Integration:**

```groovy
stage('Update GitOps Repo') {
    steps {
        script {
            sh """
                git clone https://github.com/company/gitops-repo
                cd gitops-repo

                # Update image tag
                cd apps/overlays/${ENVIRONMENT}/customer-aggregation
                kustomize edit set image \\
                    customer-aggregation=${DOCKER_REGISTRY}/${PIPELINE_NAME}:${VERSION}

                # Commit and push
                git config user.email "ci@company.com"
                git config user.name "CI Bot"
                git add .
                git commit -m "Update customer-aggregation to ${VERSION}"
                git push origin main
            """

            // Wait for ArgoCD to sync
            sh """
                argocd app wait customer-aggregation-${ENVIRONMENT} \\
                    --sync \\
                    --timeout 600
            """
        }
    }
}
```

---

## Part 12: Disaster Recovery and Business Continuity

**Question:** Final topic - how do you ensure disaster recovery for data pipelines?

**Answer:** Multi-layered DR strategy:

**1. Backup Automation:**

```yaml
# CronJob for metadata backups
apiVersion: batch/v1
kind: CronJob
metadata:
  name: backup-pipeline-metadata
spec:
  schedule: "0 */6 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: backup
              image: company/backup-tool:latest
              command:
                - /bin/sh
                - -c
                - |
                  # Backup Spark checkpoints
                  aws s3 sync s3://prod-checkpoints/ s3://backup-checkpoints/$(date +%Y%m%d-%H%M)/

                  # Backup metadata database
                  pg_dump -h postgres -U admin metastore | \
                    gzip > /tmp/metastore-$(date +%Y%m%d).sql.gz
                  aws s3 cp /tmp/metastore-*.sql.gz s3://backup-metadata/

                  # Backup pipeline configurations
                  kubectl get sparkapp -n data-pipelines-prod -o yaml | \
                    gzip > /tmp/sparkapp-$(date +%Y%m%d).yaml.gz
                  aws s3 cp /tmp/sparkapp-*.yaml.gz s3://backup-configs/
          restartPolicy: OnFailure
```

**2. Multi-Region Deployment:**

```groovy
stage('Deploy Multi-Region') {
    parallel {
        stage('Primary Region') {
            steps {
                sh """
                    kubectl --context primary-region apply -f k8s/production/
                """
            }
        }
        stage('DR Region') {
            steps {
                sh """
                    kubectl --context dr-region apply -f k8s/production/
                    kubectl --context dr-region scale sparkapp customer-aggregation --replicas=0
                """
            }
        }
    }
}
```

**3. Failover Testing:**

```python
# tests/dr/test_failover.py
def test_automated_failover():
    # Simulate primary region failure
    disable_region('us-east-1')

    # Verify traffic shifts to DR region
    time.sleep(60)
    assert get_active_region() == 'us-west-2'

    # Verify pipeline continues processing
    pipeline_status = check_pipeline_status('customer-aggregation')
    assert pipeline_status == 'RUNNING'

    # Verify data consistency
    primary_data = read_data('us-east-1', before_failover=True)
    dr_data = read_data('us-west-2', after_failover=True)
    assert compare_data(primary_data, dr_data) > 0.99
```

---

## Conclusion (5 minutes)

**Question:** Excellent answers, Answer. Before we wrap up, do you have any questions for me?

**Answer:** Yes, a few:

1. What's the current state of your CI/CD maturity for data pipelines? Are you starting from scratch or optimizing existing pipelines?

2. What are your biggest pain points currently? Deployment speed, reliability, cost, or something else?

3. How large is the data engineering team, and what's the ratio of platform engineers to data engineers?

4. What's your incident response process like for failed pipelines?

5. Are there any specific compliance requirements (GDPR, HIPAA, SOC 2) that heavily influence your CI/CD design?

**Question:** Great questions. We're at an intermediate maturity level - we have basic CI/CD but need optimization and standardization across 50+ pipelines. Our biggest pain points are deployment reliability and cost control. We have a team of 4 platform engineers supporting 20 data engineers. For incidents, we're building out our runbook automation. And yes, we're SOC 2 compliant with some GDPR requirements.

Your experience aligns really well with what we need. The team will be in touch with next steps. Thanks for your time today, Answer!

**Answer:** Thank you, Question. I'm excited about the opportunity and look forward to hearing from you!

---

## Interview Summary

**Technical Depth Demonstrated:**
- Deep understanding of CI/CD principles for data engineering
- Hands-on experience with Jenkins, Kubernetes, Ansible
- Strong grasp of monitoring, security, and cost optimization
- Practical knowledge of GitOps and disaster recovery

**Key Strengths:**
- Comprehensive testing strategies
- Security-first mindset
- Cost-conscious architecture decisions
- Experience with modern DevOps tools and patterns

**Areas Covered:**
- CI/CD fundamentals and differences for data pipelines
- Jenkins pipeline architecture and optimization
- Kubernetes deployment patterns for Spark
- Ansible automation and configuration management
- Advanced deployment strategies (blue-green, canary)
- Monitoring, observability, and distributed tracing
- Security and compliance automation
- Cost optimization techniques
- Testing pyramid for data pipelines
- GitOps implementation
- Disaster recovery planning

**Recommendation:** Strong hire for Senior DevOps/Platform Engineer role.
