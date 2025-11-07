# Testing Kafka Streaming Pipelines Locally

Short summary
- Unit-test logic with in-process drivers (TopologyTestDriver for Kafka Streams).
- Component/integration tests with ephemeral brokers (Testcontainers or EmbeddedKafka).
- End-to-end tests with Docker Compose or ephemeral clusters plus Schema Registry and Kafka Connect if needed.
- Keep tests deterministic: small partitions, single broker, controlled topic creation and retention, isolated temp dirs, explicit cleanup.

Quick checklist
- Use TopologyTestDriver for pure Kafka Streams topology unit tests.
- Use Testcontainers (recommended) for realistic integration tests (works on CI, Windows via Docker Desktop/WSL2).
- Mock or run Schema Registry for Avro/Protobuf (MockSchemaRegistryClient or Testcontainers).
- Use small timeouts and short retention; reset topics between tests.
- Capture output via consumers or use in-app sinks for assertions.
- Clean temp/log dirs, stop containers, and reset offsets after each test.

1) Unit test (Kafka Streams) — TopologyTestDriver (Java)
- Fast, no network, deterministic.

```java
// ...pom/test deps: kafka-streams, kafka-streams-test-utils, junit...
Properties props = new Properties();
props.put(StreamsConfig.APPLICATION_ID_CONFIG, "test-app");
props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "dummy:9092");
props.put(StreamsConfig.STATE_DIR_CONFIG, Files.createTempDirectory("ks-state").toString());

StreamsBuilder builder = new StreamsBuilder();
// build topology: e.g., builder.stream("in").mapValues(...).to("out");
Topology topology = builder.build();

try (TopologyTestDriver driver = new TopologyTestDriver(topology, props)) {
    TestInputTopic<String, String> in = driver.createInputTopic(
        "in", new StringSerializer(), new StringSerializer());
    TestOutputTopic<String, String> out = driver.createOutputTopic(
        "out", new StringDeserializer(), new StringDeserializer());

    in.pipeInput("k1", "value1");
    List<KeyValue<String,String>> results = out.readKeyValuesToList();
    // assert results
}
```

2) Integration test — Testcontainers Kafka (JUnit 5)
- Real broker, nearly production behavior; good for producer/consumer or Streams integration.

```java
// ...test deps: org.testcontainers:kafka, junit...
@Container
public static KafkaContainer kafka = new KafkaContainer("confluentinc/cp-kafka:7.0.1")
    .withEnv("KAFKA_AUTO_CREATE_TOPICS_ENABLE", "false");

@BeforeEach
void setup() {
  String bootstrap = kafka.getBootstrapServers();
  // create topics programmatically (AdminClient) with 1 partition, replication 1
}

// Produce and consume using real clients
Producer<String,String> p = new KafkaProducer<>(Map.of(
  ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, kafka.getBootstrapServers(),
  ProducerConfig.ACKS_CONFIG, "all", ...));

Consumer<String,String> c = new KafkaConsumer<>(...);
c.subscribe(List.of("out"));
p.send(new ProducerRecord<>("in","k","v")).get();
ConsumerRecords<String,String> recs = pollUntilNonEmpty(c, Duration.ofSeconds(5));
// assert recs
```

3) End-to-end local (Docker Compose)
- Use when you need Connect, Schema Registry, or multi-broker behavior.

docker-compose.yml (minimal)
```yaml
version: '3.8'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.0.1
    environment: { ZOOKEEPER_CLIENT_PORT: 2181 }
  kafka:
    image: confluentinc/cp-kafka:7.0.1
    depends_on: [zookeeper]
    environment:
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9092
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: 'false'
  schema-registry:
    image: confluentinc/cp-schema-registry:7.0.1
    depends_on: [kafka]
    environment:
      SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS: PLAINTEXT://kafka:9092
      SCHEMA_REGISTRY_HOST_NAME: schema-registry
```

4) Common patterns & tips
- Programmatically create topics in tests (AdminClient) so tests don't rely on auto-create.
- Use single partition & replication 1 for speed and determinism.
- Use compact/local state dirs, and clear them between tests.
- For Avro/Protobuf: use MockSchemaRegistryClient for unit tests; run Schema Registry container for integration tests.
- For Spark Structured Streaming with Kafka in tests: use Testcontainers Kafka or local cluster and use small micro-batch triggers and processAllAvailable().
- On Windows CI: ensure Docker is available (Docker Desktop/WSL2) — Testcontainers requires compatible Docker.
- Make tests idempotent: use unique topic names per test (UUID suffix) and delete topics after tests.
- Keep timeouts short but safe; fail fast on waiting loops.

5) Example patterns for assertions
- Read-from-topic then assert messages (offset-aware).
- Use compacting or keyed assertions for order-insensitive checks.
- When ordering matters, add sequence numbers to messages.

6) CI guidance
- Split: fast unit tests (TopologyTestDriver / mock schema) in PRs; slower integration tests (Testcontainers/Docker Compose) run in nightly or dedicated pipeline.
- Cache Docker images to speed CI.
- Use Testcontainers reusable containers (CI runners that support it) to reduce startup time.

Summary
- Unit-test business logic with TopologyTestDriver or mocked schema clients.
- Use Testcontainers for realistic integration tests (recommended for CI).
- Use Docker Compose for full stack E2E.
- Keep tests deterministic: control topics, partitions, retention, unique names, and cleanup.

```# Testing Kafka Streaming Pipelines Locally

Short summary
- Unit-test logic with in-process drivers (TopologyTestDriver for Kafka Streams).
- Component/integration tests with ephemeral brokers (Testcontainers or EmbeddedKafka).
- End-to-end tests with Docker Compose or ephemeral clusters plus Schema Registry and Kafka Connect if needed.
- Keep tests deterministic: small partitions, single broker, controlled topic creation and retention, isolated temp dirs, explicit cleanup.

Quick checklist
- Use TopologyTestDriver for pure Kafka Streams topology unit tests.
- Use Testcontainers (recommended) for realistic integration tests (works on CI, Windows via Docker Desktop/WSL2).
- Mock or run Schema Registry for Avro/Protobuf (MockSchemaRegistryClient or Testcontainers).
- Use small timeouts and short retention; reset topics between tests.
- Capture output via consumers or use in-app sinks for assertions.
- Clean temp/log dirs, stop containers, and reset offsets after each test.

1) Unit test (Kafka Streams) — TopologyTestDriver (Java)
- Fast, no network, deterministic.

```java
// ...pom/test deps: kafka-streams, kafka-streams-test-utils, junit...
Properties props = new Properties();
props.put(StreamsConfig.APPLICATION_ID_CONFIG, "test-app");
props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "dummy:9092");
props.put(StreamsConfig.STATE_DIR_CONFIG, Files.createTempDirectory("ks-state").toString());

StreamsBuilder builder = new StreamsBuilder();
// build topology: e.g., builder.stream("in").mapValues(...).to("out");
Topology topology = builder.build();

try (TopologyTestDriver driver = new TopologyTestDriver(topology, props)) {
    TestInputTopic<String, String> in = driver.createInputTopic(
        "in", new StringSerializer(), new StringSerializer());
    TestOutputTopic<String, String> out = driver.createOutputTopic(
        "out", new StringDeserializer(), new StringDeserializer());

    in.pipeInput("k1", "value1");
    List<KeyValue<String,String>> results = out.readKeyValuesToList();
    // assert results
}
```

2) Integration test — Testcontainers Kafka (JUnit 5)
- Real broker, nearly production behavior; good for producer/consumer or Streams integration.

```java
// ...test deps: org.testcontainers:kafka, junit...
@Container
public static KafkaContainer kafka = new KafkaContainer("confluentinc/cp-kafka:7.0.1")
    .withEnv("KAFKA_AUTO_CREATE_TOPICS_ENABLE", "false");

@BeforeEach
void setup() {
  String bootstrap = kafka.getBootstrapServers();
  // create topics programmatically (AdminClient) with 1 partition, replication 1
}

// Produce and consume using real clients
Producer<String,String> p = new KafkaProducer<>(Map.of(
  ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, kafka.getBootstrapServers(),
  ProducerConfig.ACKS_CONFIG, "all", ...));

Consumer<String,String> c = new KafkaConsumer<>(...);
c.subscribe(List.of("out"));
p.send(new ProducerRecord<>("in","k","v")).get();
ConsumerRecords<String,String> recs = pollUntilNonEmpty(c, Duration.ofSeconds(5));
// assert recs
```

3) End-to-end local (Docker Compose)
- Use when you need Connect, Schema Registry, or multi-broker behavior.

docker-compose.yml (minimal)
```yaml
version: '3.8'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.0.1
    environment: { ZOOKEEPER_CLIENT_PORT: 2181 }
  kafka:
    image: confluentinc/cp-kafka:7.0.1
    depends_on: [zookeeper]
    environment:
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9092
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: 'false'
  schema-registry:
    image: confluentinc/cp-schema-registry:7.0.1
    depends_on: [kafka]
    environment:
      SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS: PLAINTEXT://kafka:9092
      SCHEMA_REGISTRY_HOST_NAME: schema-registry
```

4) Common patterns & tips
- Programmatically create topics in tests (AdminClient) so tests don't rely on auto-create.
- Use single partition & replication 1 for speed and determinism.
- Use compact/local state dirs, and clear them between tests.
- For Avro/Protobuf: use MockSchemaRegistryClient for unit tests; run Schema Registry container for integration tests.
- For Spark Structured Streaming with Kafka in tests: use Testcontainers Kafka or local cluster and use small micro-batch triggers and processAllAvailable().
- On Windows CI: ensure Docker is available (Docker Desktop/WSL2) — Testcontainers requires compatible Docker.
- Make tests idempotent: use unique topic names per test (UUID suffix) and delete topics after tests.
- Keep timeouts short but safe; fail fast on waiting loops.

5) Example patterns for assertions
- Read-from-topic then assert messages (offset-aware).
- Use compacting or keyed assertions for order-insensitive checks.
- When ordering matters, add sequence numbers to messages.

6) CI guidance
- Split: fast unit tests (TopologyTestDriver / mock schema) in PRs; slower integration tests (Testcontainers/Docker Compose) run in nightly or dedicated pipeline.
- Cache Docker images to speed CI.
- Use Testcontainers reusable containers (CI runners that support it) to reduce startup time.

Summary
- Unit-test business logic with TopologyTestDriver or mocked schema clients.
- Use Testcontainers for realistic integration tests (recommended for CI).
- Use Docker Compose for full stack E2E.
- Keep tests deterministic: control topics, partitions, retention, unique names, and cleanup.
