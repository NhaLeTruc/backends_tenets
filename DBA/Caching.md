# Caching

Caching is a technique for storing frequently accessed data in a temporary storage area, known as a cache, in order to improve the performance and scalability of a system. When data is accessed from a cache, it is typically accessed more quickly than if it were retrieved from its original location, such as a database or a file system. This can improve the performance of the system and reduce the load on its underlying data storage.

Caching is often used in web applications and other systems that need to retrieve data quickly and efficiently. For example, a web application might use a cache to store the results of common database queries, or to store the results of computationally expensive operations. This can improve the performance of the web application by allowing it to retrieve data more quickly, and can reduce the load on its underlying data storage.

For caching, you can use tools like Redis, Memcached, or other key-value stores.

## Caching strategies

There are several caching strategies worth knowing. Most common are:

- Cache-aside (lazy loading)
- Write-through
- Write-behind
- Refresh-ahead

## Distributed caches

A distributed cache is a system for storing and managing data in a distributed environment. It is a type of cache, which is a temporary storage area for frequently accessed data, that is designed to work in a distributed system, where multiple nodes or servers are used to store and manage data.

Distributed caches are used to improve the performance and scalability of distributed systems by storing data in a way that allows it to be accessed and updated quickly and efficiently. They typically use a distributed hash table (DHT) to store data across multiple nodes or servers, and to map keys to the locations of their corresponding data. This allows data to be accessed and updated in a distributed manner, and can improve the performance and scalability of the system.

## CDNs

Content delivery network is geographically distributed group of servers which work together to provide fast delivery of Internet content.

CDNs work by storing copies of content at multiple locations around the world, and by routing users requests to the nearest location that has a copy of the requested content. This can reduce the distance that data has to travel, and can improve the speed and performance of content delivery.

A CDN allows for the quick transfer of assets needed for loading Internet content including HTML pages, javascript files, stylesheets, images, and videos.

CDN can increase content availability, redundancy, improve website load times.

