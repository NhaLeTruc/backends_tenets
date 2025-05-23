# Service Discovery

Service discovery allows an application or component to discover information about their environment and neighbors. This is usually implemented as a distributed key-value store, which can also serve as a more general location to dictate configuration details. Configuring a service discovery tool allows you to separate your runtime configuration from the actual container, which allows you to reuse the same image in a number of environments.

## Service Discovery and Globally Accessible Configuration Stores

The basic idea behind service discovery is that any new instance of an application should be able to programmatically identify the details of its current environment. This is required in order for the new instance to be able to “plug in” to the existing application environment without manual intervention. Service discovery tools are generally implemented as a globally accessible registry that stores information about the instances or services that are currently operating. Most of the time, in order to make this configuration fault tolerant and scalable, the registry is distributed among the available hosts in the infrastructure.

While the primary purpose of service discovery platforms is to serve connection details to link components together, they can be used more generally to store any type of configuration. Many deployments leverage this ability by writing their configuration data to the discovery tool. If the containers are configured so that they know to look for these details, they can modify their behavior based on what they find.

## How Does Service Discovery Work?

Each service discovery tool provides an API that components can use to set or retrieve data. Because of this, for each component, the service discovery address must either be hard-coded into the application/container itself, or provided as an option at runtime. Typically the discovery service is implemented as a key-value store accessible using standard http methods.

The way a service discovery portal works is that each service, as it comes online, registers itself with the discovery tool. It records whatever information a related component might need in order to consume the service it provides. For instance, a MySQL database may register the IP address and port where the daemon is running, and optionally the username and credentials needed to sign in.

When a consumer of that service comes online, it is able to query the service discovery registry for information at a predefined endpoint. It can then interact with the components it needs based on the information it finds. One good example of this is a load balancer. It can find every backend server that it needs to feed traffic to by querying the service discovery portal and adjusting its configuration accordingly.

## How Does Configuration Storage Relate?

One key advantage of a globally distributed service discovery system is that it can store any other type of configuration data that your components might need at runtime. This means that you can extract even more configuration out of the container and into the greater execution environment.

Typically, to make this work most effectively, your applications should be designed with reasonable defaults that can be overridden at runtime by querying the configuration store. This allows you to use the configuration store similar to the way that you would use command line flags. The difference is that by utilizing a globally accessible store, you can offer the same options to each instance of your component with no additional work.

## How Does Configuration Storage Help with Cluster Management?

One function of distributed key-value stores in Docker deployments that might not be initially apparent is the storage and management of cluster membership. Configuration stores are the perfect environment for keeping track of host membership for the sake of management tools.

Some of the information that may be stored about individual hosts in a distributed key-value store are:

- Host IP addresses
- Connection information for the hosts themselves
- Arbitrary metadata and labels that can be targeted for scheduling decisions
- Role in cluster (if using a leader/follower model)

These details are probably not something that you need to be concerned with when utilizing a service discovery platform in normal circumstances, but they provide a location for management tools to query or modify information about the cluster itself.

## What About Failure Detection?

Failure detection can be implemented in a number of ways. The concern is whether, if a component fails, the discovery service will be updated to reflect the fact that it is no longer available. This type of information is vital in order to minimize application or service failures.

Many service discovery platforms allow values to be set with a configurable timeout. The component can set a value with a timeout, and ping the discovery service at regular intervals to reset the timeout. If the component fails and the timeout is reached, that instance’s connection info is removed from the store. The length of the timeout is largely a function of how quickly the application needs to respond to a component failure.

## What About Reconfiguring Services When Details Changes?

One key improvement to the basic service discovery model is that of dynamic reconfiguration. While normal service discover allows you to influence the initial configuration of components by checking the discovery information at startup, dynamic reconfiguration involves configuring your components to react to new information in the configuration store. For instance, if you implement a load balancer, a health check on the backend servers may indicate that one member of the pool is down. The running instance of the load balancer needs to be informed and needs to be able to adjust its configuration and reload to account for this.

This can be implemented in a number of ways. Since the load balancing example is one of the primary use-cases for this ability, a number of projects exist that focus exclusively on reconfiguring a load balancer when configuration changes are detected. HAProxy configuration adjustment is common due to its ubiquitousness in the load balancing space.

Certain projects are more flexible in that they can be used to trigger changes in any type of software. These tools regularly query the discovery service and when a change is detected, use templating systems to generate configuration files that incorporate the values found at the discovery endpoint. After a new configuration file is generated, the affected service is reloaded.

This type of dynamic reconfiguration requires more planning and configuration during the build process because all of these mechanisms must exist within the component’s container. This makes the component container itself responsible for adjusting its configuration. Figuring out the necessary values to write to the discovery service and designing an appropriate data structure for easy consumption is another challenge that this system requires, but the benefits and flexibility can be substantial.

## What About Security?

One concern many people have when first learning about globally accessible configuration storage is, rightfully, security. Is it really okay to store connection information into a globally accessible location?

The answer to that question largely depends on what you are choosing to place in the store and how many layers of security you deem necessary to protect your data. Almost every service discovery platform allows for encrypting connections with SSL/TLS. For some services, privacy might not be terribly important and putting the discovery service on a private network may prove satisfactory. However, most applications would probably benefit from additional security.

There are a number of different ways to address this issue, and various projects offer their own solutions. One project’s solution is to continue to allow open access to the discovery platform itself, but to encrypt the data written to it. The application consumer must have the associated key to decrypt the data it finds in the store. Other parties will not be able to access the unencrypted data.

For a different approach, some service discovery tools implement access control lists in order to divide the key space into separate zones. They can then designate ownership or access to areas based on the access requirements defined by a specific key space. This establishes an easy way of providing information for certain parties while keeping it private from others. Each component can be configured to only have access to the information it explicitly needs.

## What Are Some Common Service Discovery Tools?

Now that we’ve discussed some of the general features of service discovery tools and globally distributed key-value stores, we can mention a few of the projects that relate to these concepts.

Some of the most common service discovery tools are:

- **etcd:** This tool was created by the makers of CoreOS to provide service discovery and globally distributed configuration to both containers and the host systems themselves. It implements an http API and has a command line client available on each host machine.
- **consul:** This service discovery platform has many advanced features that make it stand out including configurable health checks, ACL functionality, HAProxy configuration, etc.
- **zookeeper:** This example is a bit older than the previous two, providing a more mature platform at the expense of some newer features.
