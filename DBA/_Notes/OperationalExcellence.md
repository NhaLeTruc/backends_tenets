# Operational Excellence & Security

## Table of Contents

- [Operational Excellence & Security](#operational-excellence--security)
  - [Table of Contents](#table-of-contents)
  - [1. Operational Excellence](#1-operational-excellence)
    - [1.1 Reliability & Resilience](#11-reliability--resilience)
      - [SLA vs SLI vs SLO](#sla-vs-sli-vs-slo)
      - [Exception Hierarchy](#exception-hierarchy)
      - [Retry Strategies](#retry-strategies)
      - [Retries Backoff](#retries-backoff)
      - [Tail-Recursive Retry Strategy](#tail-recursive-retry-strategy)
      - [Circuit Breaker](#circuit-breaker)
      - [Dead Letter Queue Pattern](#dead-letter-queue-pattern)
      - [Self Healing](#self-healing)
    - [1.2 Software Design Patterns](#12-software-design-patterns)
      - [Chain of Responsibility Pattern](#chain-of-responsibility-pattern)
      - [CQRS (Command Query Responsibility Segregation)](#cqrs-command-query-responsibility-segregation)
      - [Async Write](#async-write)
    - [1.3 Observability & Monitoring](#13-observability--monitoring)
      - [OpenTelemetry](#opentelemetry)
      - [MDC (Mapped Diagnostic Context) Propagation](#mdc-mapped-diagnostic-context-propagation)
    - [1.4 Deployment & Operations](#14-deployment--operations)
      - [Shadow JAR / Uber JAR Deployment SWOT Analysis](#shadow-jar--uber-jar-deployment-swot-analysis)
      - [Dynamic Resource Allocation Strategy](#dynamic-resource-allocation-strategy)
    - [1.5 Cost Optimization](#15-cost-optimization)
      - [Query Cost Optimization](#query-cost-optimization)
      - [Storage Tiering Strategies](#storage-tiering-strategies)
      - [Cost Monitoring & Attribution](#cost-monitoring--attribution)
    - [1.6 Documentation Practices](#16-documentation-practices)
      - [Data Dictionary Management](#data-dictionary-management)
      - [Pipeline Documentation](#pipeline-documentation)
      - [Runbook Creation](#runbook-creation)
    - [1.7 Data Migration Strategies](#17-data-migration-strategies)
      - [Zero-Downtime Migration](#zero-downtime-migration)
      - [Data Validation During Migration](#data-validation-during-migration)
      - [Migration Testing Strategies](#migration-testing-strategies)
  - [2. Security & Privacy](#2-security--privacy)
    - [2.1 Data Protection](#21-data-protection)
      - [In-Transit and In-Storage Encryption](#in-transit-and-in-storage-encryption)
      - [Tokenization vs Encryption](#tokenization-vs-encryption)
      - [AES-NI vs AES](#aes-ni-vs-aes)
      - [Format Preserving Encryption (FPE)](#format-preserving-encryption-fpe)
      - [Automatic Credential Redaction](#automatic-credential-redaction)

## 1. Operational Excellence

### 1.1 Reliability & Resilience

#### SLA vs SLI vs SLO
**Definition**: Service Level Agreement (SLA) is customer-facing contract; Service Level Indicator (SLI) is metric measuring performance; Service Level Objective (SLO) is target for SLI.

**External Resources**:
- https://cloud.google.com/architecture/defining-slos
- https://en.wikipedia.org/wiki/Service-level_agreement
- https://www.atlassian.com/incident-management/kpis/sla-vs-slo

#### Exception Hierarchy
**Definition**: Structured organization of custom and built-in exceptions in object-oriented programming, enabling precise error handling and recovery strategies.

**External Resources**:
- https://docs.oracle.com/javase/tutorial/essential/exceptions/hierarchy.html
- https://docs.python.org/3/tutorial/errors.html
- https://en.wikipedia.org/wiki/Exception_handling

#### Retry Strategies
**Definition**: Mechanisms for automatically retrying failed operations with policies (exponential backoff, jitter, max retries) to handle transient failures.

**External Resources**:
- https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
- https://en.wikipedia.org/wiki/Exponential_backoff
- https://resilience4j.readme.io/docs/retry

#### Retries Backoff
**Definition**: Progressive delay strategy between retry attempts (exponential, linear) preventing thundering herd and allowing systems to recover.

**External Resources**:
- https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
- https://www.baeldung.com/resilience4j-retry
- https://en.wikipedia.org/wiki/Exponential_backoff

#### Tail-Recursive Retry Strategy
**Definition**: Retry pattern implemented using tail recursion where the recursive call is the last operation, enabling compiler/interpreter optimization to prevent stack overflow during repeated retry attempts.

**Why Tail Recursion for Retries**:
- Stack-safe: Compiler optimizes to loop, preventing `StackOverflowError` on many retries
- Functional style: Immutable state, easier to reason about
- Composable: Naturally integrates with monadic error handling (Try, Either, IO)

**Tail Recursion Requirements**:
- Recursive call must be the **last** operation (no post-processing)
- Return value of recursive call is directly returned
- Language/runtime must support tail call optimization (TCO)

---

**Scala Implementation**:

```scala
import scala.annotation.tailrec
import scala.util.{Try, Success, Failure}
import scala.concurrent.duration._

// Basic tail-recursive retry with delay
@tailrec
def retry[A](maxAttempts: Int, delay: FiniteDuration = 1.second)
            (operation: => A): Try[A] = {
  Try(operation) match {
    case Success(result) => Success(result)
    case Failure(_) if maxAttempts > 1 =>
      Thread.sleep(delay.toMillis)
      retry(maxAttempts - 1, delay)(operation)
    case Failure(e) => Failure(e)
  }
}

// With exponential backoff
@tailrec
def retryWithBackoff[A](
  maxAttempts: Int,
  currentDelay: FiniteDuration = 100.millis,
  maxDelay: FiniteDuration = 30.seconds,
  factor: Double = 2.0
)(operation: => A): Try[A] = {
  Try(operation) match {
    case Success(result) => Success(result)
    case Failure(_) if maxAttempts > 1 =>
      Thread.sleep(currentDelay.toMillis)
      val nextDelay = (currentDelay * factor).min(maxDelay)
      retryWithBackoff(maxAttempts - 1, nextDelay, maxDelay, factor)(operation)
    case Failure(e) => Failure(e)
  }
}

// Cats Effect IO - stack-safe by design
import cats.effect.IO
import cats.effect.Temporal
import scala.concurrent.duration._

def retryIO[A](maxAttempts: Int, delay: FiniteDuration)
              (io: IO[A])(implicit T: Temporal[IO]): IO[A] = {
  io.handleErrorWith { error =>
    if (maxAttempts > 1)
      IO.sleep(delay) *> retryIO(maxAttempts - 1, delay)(io)
    else
      IO.raiseError(error)
  }
}

// ZIO - built-in retry with Schedule
import zio._

val policy = Schedule.recurs(5) && Schedule.exponential(100.millis)
val retriedEffect = myEffect.retry(policy)
```

**Scala Best Practices**:

- Always annotate with `@tailrec` to get compile-time verification
- Use `Try`, `Either`, or effect types (IO/ZIO) instead of throwing exceptions
- Prefer library solutions: `cats-retry`, `ZIO.retry`, or `fs2-retry` for production
- For async operations, use effect-based retry (IO/ZIO) which is stack-safe by construction
- Add jitter to backoff: `delay * (0.5 + Random.nextDouble() * 0.5)`
- Log attempt number for observability: pass `attempt: Int` parameter

---

**Java Implementation**:

```java
// Java doesn't have TCO - use trampolining or iteration instead

// Iterative approach (preferred in Java)
public <T> T retryWithBackoff(
    Supplier<T> operation,
    int maxAttempts,
    Duration initialDelay,
    double backoffFactor
) throws Exception {
    Duration delay = initialDelay;
    Exception lastException = null;

    for (int attempt = 1; attempt <= maxAttempts; attempt++) {
        try {
            return operation.get();
        } catch (Exception e) {
            lastException = e;
            if (attempt < maxAttempts) {
                Thread.sleep(delay.toMillis());
                delay = Duration.ofMillis((long)(delay.toMillis() * backoffFactor));
            }
        }
    }
    throw lastException;
}

// Trampoline pattern for functional style
public abstract class Trampoline<T> {
    public abstract T get();
    public abstract boolean isComplete();
    public abstract Trampoline<T> next();

    public static <T> Trampoline<T> done(T value) {
        return new Trampoline<T>() {
            public T get() { return value; }
            public boolean isComplete() { return true; }
            public Trampoline<T> next() { throw new UnsupportedOperationException(); }
        };
    }

    public static <T> Trampoline<T> more(Supplier<Trampoline<T>> next) {
        return new Trampoline<T>() {
            public T get() { throw new UnsupportedOperationException(); }
            public boolean isComplete() { return false; }
            public Trampoline<T> next() { return next.get(); }
        };
    }

    public T run() {
        Trampoline<T> current = this;
        while (!current.isComplete()) {
            current = current.next();
        }
        return current.get();
    }
}

// Using Vavr for functional retry
import io.vavr.control.Try;

Try<String> result = Try.of(() -> riskyOperation())
    .recoverWith(e -> Try.of(() -> riskyOperation()))  // Limited, not tail-recursive
    .recoverWith(e -> Try.of(() -> riskyOperation()));

// Resilience4j (recommended for production)
import io.github.resilience4j.retry.Retry;
import io.github.resilience4j.retry.RetryConfig;

RetryConfig config = RetryConfig.custom()
    .maxAttempts(5)
    .waitDuration(Duration.ofMillis(100))
    .exponentialBackoffMultiplier(2.0)
    .retryExceptions(IOException.class, TimeoutException.class)
    .build();

Retry retry = Retry.of("myRetry", config);
Supplier<String> decorated = Retry.decorateSupplier(retry, this::callService);
```

**Java Best Practices**:

- Use iterative loops instead of recursion (JVM lacks TCO)
- For functional style, use Trampoline pattern or `CompletableFuture` chains
- Prefer Resilience4j or Spring Retry for production workloads
- With CompletableFuture, chain retries with `.exceptionallyCompose()`
- Use `ScheduledExecutorService` for non-blocking delays
- Consider Project Reactor's `retryWhen()` for reactive streams

---

**Python Implementation**:

```python
# Python has no TCO, but we can use decorators and iteration

import time
import random
from functools import wraps
from typing import TypeVar, Callable, Optional, Type, Tuple

T = TypeVar('T')

# Decorator-based retry with backoff
def retry(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    jitter: bool = True
):
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            delay = initial_delay
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        sleep_time = delay
                        if jitter:
                            sleep_time *= (0.5 + random.random())
                        time.sleep(sleep_time)
                        delay = min(delay * backoff_factor, max_delay)

            raise last_exception
        return wrapper
    return decorator

# Usage
@retry(max_attempts=5, initial_delay=0.5, exceptions=(ConnectionError, TimeoutError))
def fetch_data(url: str) -> dict:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


# Async retry for asyncio
import asyncio

def async_retry(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        await asyncio.sleep(delay * (0.5 + random.random()))
                        delay *= backoff_factor

            raise last_exception
        return wrapper
    return decorator

@async_retry(max_attempts=3, exceptions=(aiohttp.ClientError,))
async def async_fetch(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


# Using tenacity library (recommended)
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
import logging

logger = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=60),
    retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def reliable_operation():
    return external_service.call()


# Generator-based "trampoline" pattern
def trampoline(gen):
    """Execute a generator as a trampoline for stack-safety."""
    stack = [gen]
    result = None
    while stack:
        try:
            result = stack[-1].send(result)
            if hasattr(result, '__next__'):
                stack.append(result)
                result = None
        except StopIteration as e:
            stack.pop()
            result = e.value
    return result

def retry_gen(operation, max_attempts, delay):
    """Generator-based retry using trampoline."""
    for attempt in range(max_attempts):
        try:
            return operation()
        except Exception as e:
            if attempt < max_attempts - 1:
                time.sleep(delay)
                yield  # Trampoline bounce point
            else:
                raise

# result = trampoline(retry_gen(risky_op, 5, 1.0))
```

**Python Best Practices**:

- Use `tenacity` library for production (feature-rich, well-tested)
- CPython doesn't optimize tail calls - use iteration or generators
- For async code, use `asyncio.sleep()` for non-blocking delays
- Add logging with attempt numbers: `before_sleep_log()` in tenacity
- Set `max_delay` cap to prevent unbounded exponential growth
- Use type hints for better IDE support and documentation
- Consider `backoff` library as simpler alternative to tenacity

---

**General Guidelines**:

1. **Language TCO Support**:

   | Language | TCO Support | Recommendation |
   | --- | --- | --- |
   | Scala | Yes (with @tailrec) | Use tail recursion |
   | Java | No | Use iteration or Trampoline |
   | Python | No (CPython) | Use iteration or generators |
   | Kotlin | Yes (tailrec keyword) | Use tail recursion |

2. **Backoff Strategies**:
   - **Exponential**: `delay * (2 ^ attempt)` - standard for network retries
   - **Linear**: `delay * attempt` - gentler ramp-up
   - **Decorrelated jitter**: `min(cap, random(base, prev_delay * 3))` - AWS recommended

3. **Retry Budget**:
   - Set maximum total retry time, not just attempt count
   - Example: 5 attempts OR 30 seconds total, whichever comes first

4. **Idempotency Requirement**:
   - Only retry operations that are safe to repeat
   - Use idempotency keys for mutating operations

5. **Error Classification**:
   - Retry: network errors, 503, 429, connection reset, timeout
   - Don't retry: 4xx client errors, validation failures, auth errors

**External Resources**:

- <https://en.wikipedia.org/wiki/Tail_call>
- <https://docs.scala-lang.org/tour/tail-recursion.html>
- <https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/>
- <https://tenacity.readthedocs.io/>
- <https://github.com/cb372/cats-retry>

#### Circuit Breaker
**Definition**: Fault tolerance pattern that prevents cascading failures by stopping requests to failing services and gradually reopening when health improves.

**Circuit States**:
- **Closed**: Normal operation; requests pass through, failures counted
- **Open**: Circuit tripped; requests fail fast without calling downstream
- **Half-Open**: Testing recovery; limited requests allowed to probe health

**Key Configuration Parameters**:

| Parameter | Description | Typical Value |
| --- | --- | --- |
| Failure threshold | Failures before opening circuit | 5-10 failures or 50% rate |
| Timeout duration | How long circuit stays open | 30-60 seconds |
| Half-open requests | Probes allowed in half-open state | 3-5 requests |
| Sliding window | Time/count window for failure tracking | 10-100 calls or 10-60s |
| Slow call threshold | Response time considered "slow" | 2-5 seconds |

---

**Scala Implementation (Akka/Resilience4j)**:

```scala
// Akka Circuit Breaker
import akka.pattern.CircuitBreaker
import scala.concurrent.duration._

val breaker = CircuitBreaker(
  scheduler = system.scheduler,
  maxFailures = 5,
  callTimeout = 10.seconds,
  resetTimeout = 30.seconds
).onOpen(logger.warn("Circuit opened"))
 .onHalfOpen(logger.info("Circuit half-open"))
 .onClose(logger.info("Circuit closed"))

// Usage with Future
breaker.withCircuitBreaker(callExternalService())

// Cats Effect + Resilience4j wrapper
import io.github.resilience4j.circuitbreaker.CircuitBreaker
import cats.effect.IO

def withBreaker[A](cb: CircuitBreaker)(io: IO[A]): IO[A] =
  IO.defer {
    if (cb.tryAcquirePermission()) {
      io.attempt.flatMap {
        case Right(a) => IO(cb.onSuccess(0, TimeUnit.NANOSECONDS)) *> IO.pure(a)
        case Left(e)  => IO(cb.onError(0, TimeUnit.NANOSECONDS, e)) *> IO.raiseError(e)
      }
    } else IO.raiseError(CallNotPermittedException.createCallNotPermittedException(cb))
  }
```

**Scala Best Practices**:
- Use `withCircuitBreaker` for Future-based code; wrap with custom combinator for IO/ZIO
- Leverage `onOpen`/`onClose` callbacks for metrics emission (Prometheus, StatsD)
- Combine with `retry` and `timeout` for comprehensive resilience
- For ZIO: use `zio-resilience` or native `ZIO.timeout` + custom state machine
- Consider `CircuitBreaker.of[F]` from `cats-retry` for tagless final style

---

**Java Implementation (Resilience4j)**:

```java
// Resilience4j Circuit Breaker
import io.github.resilience4j.circuitbreaker.CircuitBreaker;
import io.github.resilience4j.circuitbreaker.CircuitBreakerConfig;
import io.github.resilience4j.circuitbreaker.CircuitBreakerRegistry;

CircuitBreakerConfig config = CircuitBreakerConfig.custom()
    .failureRateThreshold(50)                     // 50% failure rate triggers open
    .slowCallRateThreshold(50)                    // 50% slow calls triggers open
    .slowCallDurationThreshold(Duration.ofSeconds(2))
    .waitDurationInOpenState(Duration.ofSeconds(30))
    .permittedNumberOfCallsInHalfOpenState(3)
    .slidingWindowType(SlidingWindowType.COUNT_BASED)
    .slidingWindowSize(10)
    .minimumNumberOfCalls(5)                      // Minimum calls before calculating rate
    .recordExceptions(IOException.class, TimeoutException.class)
    .ignoreExceptions(BusinessException.class)   // Don't count as failures
    .build();

CircuitBreakerRegistry registry = CircuitBreakerRegistry.of(config);
CircuitBreaker breaker = registry.circuitBreaker("externalService");

// Decorating a supplier
Supplier<String> decorated = CircuitBreaker
    .decorateSupplier(breaker, () -> externalService.call());

// With Spring Boot annotation
@CircuitBreaker(name = "backendA", fallbackMethod = "fallback")
public String callService() {
    return restTemplate.getForObject("/api/data", String.class);
}

public String fallback(Exception e) {
    return "Cached or default response";
}
```

**Java Best Practices**:
- Use `CircuitBreakerRegistry` for centralized management and metrics
- Configure `recordExceptions` explicitly; don't circuit-break on validation errors
- Combine with `@Retry`, `@RateLimiter`, `@Bulkhead` annotations (order matters)
- Expose actuator endpoints: `/actuator/circuitbreakers`, `/actuator/circuitbreakerevents`
- Use `TimeLimiter` alongside circuit breaker to enforce timeouts
- For reactive: use `Resilience4jRxJava2` or `reactor-resilience4j` operators

---

**Python Implementation (pybreaker/tenacity)**:

```python
# pybreaker - Dedicated circuit breaker library
import pybreaker
import logging

class LogListener(pybreaker.CircuitBreakerListener):
    def state_change(self, breaker, old_state, new_state):
        logging.warning(f"Circuit {breaker.name}: {old_state} -> {new_state}")

    def failure(self, breaker, exception):
        logging.error(f"Circuit {breaker.name} recorded failure: {exception}")

breaker = pybreaker.CircuitBreaker(
    fail_max=5,                    # Failures before opening
    reset_timeout=30,              # Seconds before half-open
    exclude=[ValueError],          # Don't count these as failures
    listeners=[LogListener()]
)

@breaker
def call_external_service():
    response = requests.get("https://api.example.com/data", timeout=5)
    response.raise_for_status()
    return response.json()

# Manual state check
if breaker.current_state == "open":
    return cached_response()

# Async support with aiobreaker
import aiobreaker

async_breaker = aiobreaker.CircuitBreaker(fail_max=5, timeout_duration=30)

@async_breaker
async def async_call():
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()

# tenacity with circuit breaker pattern
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((ConnectionError, TimeoutError))
)
def resilient_call():
    return requests.get(url, timeout=5).json()
```

**Python Best Practices**:
- Use `pybreaker` for dedicated circuit breaker; `tenacity` for retry-focused resilience
- Set appropriate `exclude` list to avoid breaking on client errors (4xx)
- Implement `CircuitBreakerListener` for observability (Prometheus push, logging)
- For async code, use `aiobreaker` or implement with `asyncio.Lock` + state machine
- Combine with `functools.lru_cache` for fallback responses
- In FastAPI/Django: create middleware or dependency injection pattern

---

**General Guidelines**:

1. **Failure Classification**:
   - Circuit-break on: network errors, timeouts, 5xx responses, connection refused
   - Don't circuit-break on: 4xx client errors, validation failures, auth errors

2. **Timeout Coordination**:
   - Set circuit breaker timeout > individual request timeout
   - Example: request timeout 5s, circuit timeout 30s, retry budget 3 attempts

3. **Monitoring & Alerting**:
   - Alert on circuit open events (indicates downstream issues)
   - Track: state transitions, failure rates, response times, rejected calls
   - Dashboard per-service circuit health

4. **Fallback Strategies**:
   - Return cached data (stale-while-revalidate pattern)
   - Serve degraded response (fewer features, default values)
   - Queue for later retry (if operation is idempotent)
   - Fail fast with meaningful error message

5. **Testing**:
   - Unit test each state transition
   - Chaos testing: inject failures to verify circuit opens
   - Load test half-open behavior under traffic

**External Resources**:
- https://martinfowler.com/bliki/CircuitBreaker.html
- https://resilience4j.readme.io/docs/circuitbreaker
- https://doc.akka.io/docs/akka/current/common/circuitbreaker.html
- https://pybreaker.readthedocs.io/
- https://github.com/fabfuel/circuitbreaker

#### Dead Letter Queue Pattern
**Definition**: Messaging pattern routing messages that cannot be processed to dedicated queues for later analysis, preventing poison messages from blocking processing.

**External Resources**:
- https://aws.amazon.com/blogs/architecture/handling-poison-pills-in-queues/
- https://en.wikipedia.org/wiki/Dead_letter_queue
- https://docs.spring.io/spring-cloud-stream/docs/current/reference/html/spring-cloud-stream.html#spring-cloud-stream-overview-error-handling

#### Self Healing
**Definition**: Systems that automatically detect and recover from failures through health checks, auto-recovery, and self-restoration mechanisms.

**External Resources**:
- https://www.gartner.com/en/research
- https://www.ibm.com/cloud/learn/self-healing-systems
- https://en.wikipedia.org/wiki/Autonomic_computing

### 1.2 Software Design Patterns

#### Chain of Responsibility Pattern
**Definition**: Behavioral pattern where multiple handlers process a request in sequence, each deciding whether to handle or pass to the next handler.

**External Resources**:
- https://refactoring.guru/design-patterns/chain-of-responsibility
- https://en.wikipedia.org/wiki/Chain-of-responsibility_pattern
- https://www.geeksforgeeks.org/chain-responsibility-pattern/

#### CQRS (Command Query Responsibility Segregation)
**Definition**: Architectural pattern separating read and write models, optimizing each independently for different workloads and enabling eventual consistency.

**External Resources**:
- https://martinfowler.com/bliki/CQRS.html
- https://docs.microsoft.com/en-us/azure/architecture/patterns/cqrs
- https://www.youtube.com/watch?v=qDlN-_L4l8A

#### Async Write
**Definition**: Pattern executing write operations asynchronously without blocking callers, improving responsiveness through eventual consistency guarantees.

**External Resources**:
- https://martinfowler.com/bliki/EventSourcing.html
- https://www.mongodb.com/docs/manual/core/write-operations-atomicity/
- https://en.wikipedia.org/wiki/Eventual_consistency

### 1.3 Observability & Monitoring

#### OpenTelemetry
**Definition**: Open standard for collecting metrics, logs, and traces from applications, enabling vendor-agnostic observability across distributed systems.

**External Resources**:
- https://opentelemetry.io/
- https://opentelemetry.io/docs/
- https://www.youtube.com/watch?v=r8UvWSX3KA8

#### MDC (Mapped Diagnostic Context) Propagation
**Definition**: Technique storing context information (request IDs, user IDs) in thread-local storage and propagating across service calls for distributed tracing.

**External Resources**:
- https://logback.qos.ch/manual/mdc.html
- https://slf4j.org/manual.html#mdc
- https://www.geeksforgeeks.org/mapped-diagnostic-context-mdc/

### 1.4 Deployment & Operations

#### Shadow JAR / Uber JAR Deployment SWOT Analysis
**Definition**: JAR packaging strategies - Shadow JAR bundles dependencies; Uber JAR creates single executable JAR. SWOT comparison of tradeoffs.

**Strategy Overview**:
| Strategy | Tool | Approach |
|----------|------|----------|
| **Shadow JAR** | Gradle Shadow Plugin | Bundles + relocates (shades) dependency packages to avoid conflicts |
| **Uber JAR** | Maven Assembly/Shade | Bundles all dependencies into single JAR without relocation |
| **Thin JAR** | Standard build | Application code only; dependencies resolved at runtime |

---

**Shadow JAR SWOT**:

| Strengths | Weaknesses |
|-----------|------------|
| Package relocation prevents classpath conflicts | Complex configuration for proper shading rules |
| Solves "dependency hell" in shared environments | Larger build times due to bytecode rewriting |
| Works reliably with Spark/Hadoop clusters | Debugging harder (relocated stack traces) |
| Gradle-native with good incremental build support | Some reflection-based libraries break when shaded |

| Opportunities | Threats |
|---------------|---------|
| Growing Kotlin/Gradle ecosystem adoption | GraalVM native-image as lighter alternative |
| Kubernetes jobs prefer self-contained artifacts | JPMS split-package issues in Java 9+ |
| Serverless cold-start optimization | Maintenance burden if Shadow plugin deprecated |

---

**Uber JAR (Maven Shade/Assembly) SWOT**:

| Strengths | Weaknesses |
|-----------|------------|
| Maven ecosystem maturity and wide adoption | No relocation = version conflicts still possible |
| Simple configuration for basic use cases | Service loader files (META-INF/services) require merging |
| Single artifact simplifies deployment | Duplicate class warnings often ignored |
| Well-documented with extensive examples | Large artifacts slow CI/CD pipelines |

| Opportunities | Threats |
|---------------|---------|
| Spring Boot fat JAR approach widely understood | License compliance issues with bundled deps |
| Standard approach for legacy Java shops | Supply chain attacks via embedded libraries |
| Easy migration path from thin JAR | Vulnerability scanners may miss shaded CVEs |

---

**Thin JAR SWOT**:

| Strengths | Weaknesses |
|-----------|------------|
| Small artifact size (KB vs MB) | Requires dependency management at runtime |
| Fast builds (no repackaging overhead) | "Works on my machine" deployment issues |
| Easy to patch individual libraries | Complex classpath configuration |
| Better for shared library environments | Version conflicts between applications |

| Opportunities | Threats |
|---------------|---------|
| Application server deployments (WildFly, etc.) | Decreasing relevance in container-first world |
| Memory-efficient when libs shared across apps | OSGi complexity often not worth investment |
| Hot-deploy capabilities | Reproducibility challenges |

---

**Decision Matrix**:

| Use Case | Recommended Strategy |
|----------|---------------------|
| Spark/Flink job submission | Shadow JAR (relocation critical) |
| Spring Boot microservice | Uber JAR (spring-boot-maven-plugin) |
| AWS Lambda / serverless | Shadow JAR or Uber JAR |
| Application server (JBoss, WebLogic) | Thin JAR |
| CLI tool distribution | Shadow JAR |
| Library published to Maven Central | Thin JAR (never shade a library) |
| Monorepo with shared dependencies | Thin JAR + dependency management |

**External Resources**:
- https://imperceptiblethoughts.com/shadow/introduction/
- https://maven.apache.org/plugins/maven-assembly-plugin/
- https://github.com/johnrengelman/shadow

#### Dynamic Resource Allocation Strategy
**Definition**: Cluster resource management dynamically adjusting executor/core allocation based on workload demands, optimizing utilization and cost.

**External Resources**:
- https://spark.apache.org/docs/latest/configuration.html#dynamic-allocation
- https://databricks.com/blog/2022/10/24/dynamic-resource-allocation-for-spark.html
- https://www.youtube.com/watch?v=daXEp4HmS-E

### 1.5 Cost Optimization

#### Query Cost Optimization
**Definition**: Techniques for reducing compute costs in cloud data warehouses where pricing is based on data scanned or compute time.

**BigQuery Cost Optimization**:
- Use partitioned and clustered tables
- Avoid SELECT * (specify columns)
- Use LIMIT in development, remove in production
- Leverage cached results
- Monitor with INFORMATION_SCHEMA.JOBS

**Snowflake Cost Optimization**:
- Right-size virtual warehouses
- Use auto-suspend and auto-resume
- Leverage result caching
- Monitor with ACCOUNT_USAGE.QUERY_HISTORY
- Use resource monitors and alerts

**Redshift Cost Optimization**:
- Choose appropriate node types (RA3 vs DC2)
- Use Redshift Spectrum for cold data
- Vacuum and analyze regularly
- Monitor with STL_QUERY and SVL_QUERY_SUMMARY

**External Resources**:
- https://cloud.google.com/bigquery/docs/best-practices-costs
- https://docs.snowflake.com/en/user-guide/cost-understanding-overall
- https://docs.aws.amazon.com/redshift/latest/dg/c-optimizing-query-performance.html

#### Storage Tiering Strategies
**Definition**: Moving data between storage tiers (hot, warm, cold, archive) based on access patterns to optimize cost while maintaining accessibility.

**Tiering Framework**:
- **Hot**: Frequently accessed, SSD/high-performance storage
- **Warm**: Occasionally accessed, standard storage
- **Cold**: Rarely accessed, lower-cost storage
- **Archive**: Compliance/historical, lowest cost, retrieval latency acceptable

**Implementation Approaches**:
- Time-based policies (move data older than X days)
- Access-based policies (move data not accessed in X days)
- Hybrid approaches based on data importance

**External Resources**:
- https://cloud.google.com/storage/docs/storage-classes
- https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html
- https://docs.snowflake.com/en/user-guide/data-time-travel

#### Cost Monitoring & Attribution
**Definition**: Tracking and attributing data platform costs to teams, projects, or use cases for accountability and optimization.

**Cost Attribution Methods**:
- Resource tagging (by team, project, environment)
- Query-level attribution (BigQuery labels, Snowflake query tags)
- Chargeback/showback models
- Budget alerts and anomaly detection

**External Resources**:
- https://docs.snowflake.com/en/user-guide/resource-monitors
- https://cloud.google.com/billing/docs/how-to/budgets
- https://aws.amazon.com/aws-cost-management/aws-cost-explorer/

### 1.6 Documentation Practices

#### Data Dictionary Management
**Definition**: Maintaining comprehensive documentation of data assets including table descriptions, column definitions, business context, and ownership.

**Data Dictionary Components**:
- Table descriptions and business purpose
- Column definitions with data types and constraints
- Business glossary mapping technical to business terms
- Data lineage (source systems, transformations)
- Ownership and stewardship information
- Update frequency and SLAs

**External Resources**:
- https://www.getdbt.com/blog/data-dictionary-best-practices/
- https://www.alation.com/blog/what-is-a-data-dictionary/
- https://dataedo.com/blog/what-is-data-dictionary

#### Pipeline Documentation
**Definition**: Documenting data pipeline architecture, dependencies, configurations, and operational procedures for maintainability.

**Documentation Elements**:
- Pipeline architecture diagrams
- Input/output specifications
- Configuration parameters and defaults
- Error handling and recovery procedures
- Performance benchmarks and SLAs
- Troubleshooting guides

**External Resources**:
- https://docs.getdbt.com/docs/build/documentation
- https://www.astronomer.io/blog/documenting-airflow-pipelines/
- https://c4model.com/

#### Runbook Creation
**Definition**: Operational guides documenting procedures for routine tasks, incident response, and troubleshooting for on-call engineers.

**Runbook Components**:
- Incident identification and classification
- Step-by-step resolution procedures
- Escalation paths and contacts
- Common issues and solutions
- Post-incident review templates

**External Resources**:
- https://www.atlassian.com/incident-management/on-call/runbooks
- https://sre.google/sre-book/effective-troubleshooting/
- https://www.pagerduty.com/resources/learn/what-is-a-runbook/


### 1.7 Data Migration Strategies

#### Zero-Downtime Migration
**Definition**: Migration strategies allowing continuous data access and processing during platform or schema changes.

**Approaches**:
- **Dual-Write**: Write to both old and new systems simultaneously
- **Change Data Capture (CDC)**: Stream changes to new system
- **Blue-Green**: Switch traffic between parallel environments
- **Strangler Fig**: Gradually route traffic to new system

**External Resources**:
- https://martinfowler.com/bliki/StranglerFigApplication.html
- https://www.confluent.io/blog/data-migration-using-change-data-capture/
- https://aws.amazon.com/blogs/database/database-migration-strategies/

#### Data Validation During Migration
**Definition**: Verification techniques ensuring data completeness, accuracy, and consistency between source and target systems during migration.

**Validation Checks**:
- Row count comparisons
- Aggregate value comparisons (sums, averages)
- Sample record comparison (hash-based or random)
- Referential integrity validation
- Business rule validation

**External Resources**:
- https://docs.greatexpectations.io/docs/tutorials/getting_started/
- https://www.soda.io/resources/how-to-validate-data-during-migration
- https://aws.amazon.com/dms/resources/

#### Migration Testing Strategies
**Definition**: Testing approaches ensuring migration correctness before, during, and after cutover.

**Testing Phases**:
- **Pre-Migration**: Schema compatibility, capacity planning, dry runs
- **During Migration**: Real-time validation, progress monitoring, rollback testing
- **Post-Migration**: Full data validation, performance testing, user acceptance

**External Resources**:
- https://cloud.google.com/architecture/database-migration-concepts-principles
- https://docs.aws.amazon.com/dms/latest/userguide/CHAP_BestPractices.html
- https://www.postgresql.org/docs/current/migration.html

---

## 2. Security & Privacy

### 2.1 Data Protection

#### In-Transit and In-Storage Encryption
**Definition**: Encryption at two layers - data in transit uses TLS/SSL; data at rest uses encryption algorithms (AES) to protect stored data.

**External Resources**:
- https://en.wikipedia.org/wiki/Encryption
- https://aws.amazon.com/compliance/encryption/
- https://www.owasp.org/index.php/Transport_Layer_Protection_Cheat_Sheet

#### Tokenization vs Encryption
**Definition**: Tokenization replaces sensitive data with non-sensitive tokens stored in separate vault; encryption uses keys to encode/decode data.

**External Resources**:
- https://www.tokenization.com/
- https://en.wikipedia.org/wiki/Tokenization_(data_security)
- https://www.owasp.org/index.php/PCI_DSS_Tokenization

#### AES-NI vs AES
**Definition**: AES is encryption standard; AES-NI is Intel CPU instruction set accelerating AES operations dramatically for hardware-based encryption.

**External Resources**:
- https://en.wikipedia.org/wiki/AES_instruction_set
- https://www.intel.com/content/www/us/en/architecture-and-technology/aes-ni.html
- https://security.stackexchange.com/questions/208919/does-aes-ni-actually-make-aes-faster

#### Format Preserving Encryption (FPE)
**Definition**: Encryption technique maintaining data format (SSN still looks like SSN), enabling column-level encryption without schema changes.

**External Resources**:
- https://en.wikipedia.org/wiki/Format-preserving_encryption
- https://csrc.nist.gov/publications/detail/sp/800-38g/final
- https://stackoverflow.com/questions/53503906/format-preserving-encryption-implementation

#### Automatic Credential Redaction
**Definition**: Security practice automatically removing or masking sensitive credentials from logs, error messages, and system output.

**External Resources**:
- https://owasp.org/www-community/attacks/Log_Injection
- https://github.com/coveo/redaction-engine
- https://www.splunk.com/en_us/blog/security/credit-cards-redaction.html

---
