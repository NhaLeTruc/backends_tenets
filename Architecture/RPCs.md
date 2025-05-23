# Remote Procedure Call

RPC (Remote Procedure Call) and REST (Representational State Transfer) are two distinct architectural styles for building APIs, each with its strengths and weaknesses. RPC focuses on calling specific functions or procedures on a remote server, while REST emphasizes the manipulation of resources represented by URIs, with a focus on statelessness and HTTP methods.

RPC (Remote Procedure Call) APIs offer advantages in high-performance scenarios and tight integration with existing systems, but they come with drawbacks related to coupling, discoverability, and standardization compared to RESTful APIs.

## RPC

- **Focus:** RPC APIs focus on calling specific functions or actions on a remote server.
- **Data Format:** Often uses byte formats for data transfer.
- **Communication:** Primarily uses synchronous communication.
- **Implementation:** Can be simpler to implement, allowing you to add functions/endpoints easily.
- **Use Cases:** Well-suited for internal systems, high-performance scenarios, and operations that require low-latency writes.

## REST

- **Focus:** REST APIs focus on interacting with resources represented by URIs, allowing clients to perform CRUD (Create, Read, Update, Delete) operations.
- **Data Format:** Can handle various data formats, including JSON and XML.
- **Communication:** Uses HTTP methods like GET, POST, PUT, DELETE to interact with resources.
- **Implementation:** May seem more complex than RPC, but offers flexibility and scalability.
- **Use Cases:** Commonly used for web services, microservices architectures, and applications that benefit from statelessness and scalability.

## Key Differences

- **Resource vs. Action:** REST operates on resources, while RPC focuses on actions.
- **Statelessness:** REST is designed to be stateless, meaning each request contains all the necessary information.
- **HTTP Methods:** REST uses HTTP methods to perform operations on resources, while RPC often uses custom methods.
- **Data Format:** REST can use various data formats, while RPC often uses byte formats.
- **Performance:** RPC can be more performant for low-latency operations, while REST excels in scalability and flexibility.

## In Summary

- Choose RPC if you need a simple, high-performance API for internal systems or specific operations.
- Choose REST if you need a flexible, scalable, and stateless API for web services and microservices architectures.

## Advantages of RPC APIs

- **Granular Control/Power:** RPC allows for fine-grained control over the API, enabling developers to implement complex logic and operations efficiently.
- **Tight Coupling:** RPC's direct function invocation leads to tighter coupling between client and server, which can be beneficial for performance in specific use cases.
- **High Performance:** In scenarios where performance and efficiency are crucial, RPC can offer advantages due to its direct function call model.
- **Mature Ecosystem: RPC has a well-established ecosystem and is often used in various internal systems and applications.
- **Clear Interface Definition:** RPC interfaces are often clearly defined, making it easier to understand and use the API.

## Disadvantages of RPC APIs

- **Coupling:** RPC can lead to tighter coupling between client and server, making it harder to maintain and evolve the system.
- **Discoverability:** RPC interfaces can be less discoverable than REST APIs, requiring more documentation and developer support.
- **Standardization:** RPC is not as standardized as REST, meaning implementations can vary, leading to potential integration challenges.
- **Complexity:** RPC can be more complex to implement and maintain compared to REST APIs, particularly for larger systems.
- **Less Flexible:** RPC is primarily suited for function calls, which may not be ideal for general resource manipulation.

## Reference

1. [soap-vs-rest-vs-graphql-vs-rpc](https://wezom.com/blog/comparing-api-architectural-styles-soap-vs-rest-vs-graphql-vs-rpc)
2. [rpc-and-rest](https://aws.amazon.com/compare/the-difference-between-rpc-and-rest/)
