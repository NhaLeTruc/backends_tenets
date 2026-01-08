# Hexagonal Architecture

Hexagonal Architecture (or Ports & Adapters) is a software design pattern that isolates an application's core business logic from external concerns (UI, database, APIs) using interfaces called Ports, with Adapters translating data between the core and specific technologies, creating loosely coupled, testable systems where core logic remains independent of frameworks and infrastructure. Dependencies flow inwards, protecting the inner core, allowing easy swapping of external components like databases or UIs without affecting business rules.

## Core Concepts

- **Application Core (Inside the Hexagon)**: Contains the heart of the system—the domain model and business logic, free from external technology details.
- **Ports (Interfaces)**: Abstract contracts defining how the core interacts with the outside world (e.g., UserRepository interface, CreateUserCommand interface).
- **Adapters (Implementations)**: Translate external data/requests into port calls and vice versa. They sit on the outside, connecting to specific technologies.

## Types of Adapters & Ports

- **Driving (Primary) Adapters**: Initiate actions on the application (e.g., REST API controller, CLI, Web UI).
- **Driven (Secondary) Adapters**: Respond to requests from the application (e.g., Database Repository implementation, Message Queue sender).
- **Inbound Ports**: Define how external actors drive the application (e.g., UserService interface for incoming commands).
- **Outbound Ports**: Define how the application drives external systems (e.g., NotificationService interface for sending emails).

## Key Benefits

- **Decoupling & Flexibility**: Easily switch databases (SQL to NoSQL), UIs (Web to Mobile), or message queues without touching core logic.
- **Testability**: The core can be tested in isolation using mock adapters, ensuring business rules are correct.
- **Technology Independence**: Delays technology choices, preventing premature lock-in.
- **Portability**: Adapters allow the same core to run in different environments (e.g., Lambda, containers).

## How it Works (Data Flow Example)

1. A REST Controller (Driving Adapter) receives an HTTP request (e.g., POST /users with JSON data).
2. The adapter translates the JSON into a domain-specific object (e.g., CreateUserCommand) and calls the corresponding Inbound Port (e.g., UserService.createUser(command)).
3. The core logic processes the request, potentially saving data via an Outbound Port (e.g., UserRepository.save(user)), which the core only knows as an interface.
4. A Database Repository (Driven Adapter) implements the UserRepository port, handling the actual database save (e.g., to PostgreSQL).
5. The core returns a result, which the REST Adapter translates back into an HTTP response (e.g., 201 Created or 400 Bad Request).
