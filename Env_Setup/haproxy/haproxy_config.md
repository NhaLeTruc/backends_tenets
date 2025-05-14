# HAProxy configuration

Use the HAProxy configuration file to define all aspects of the load balancer function, such as:

- Is the incoming stream treated as UDP, TCP, or HTTP?
- What sort of authentication is applied?
- Should supplemental security modules such as bot management, firewall, or captcha be applied?
- What about other supplemental modules, such as geolocation, device detection, or SNMP?
- Should metrics influence whether to deny or allow a request?
- Which backend servers should service the request?
- What log output do you need?

The configuration file can be simple or quite complex, depending on your needs.

## HAProxy Configuration file

> /etc/haproxy/haproxy.cfg

An HAProxy configuration file is composed of sections like **frontend**, **backend**, **defaults**, and **global**.

Section headers begin at the start of a line, and all configuration directives of a section should be indented for readability. Except for global, you can set multiple sections of the same type, such as to load balance different websites and define different pools of backend servers.

You can enable extra functionality by using the various other sections, such as mailers, peers, and resolvers, which we describe in other parts of this guide.

The main sections of the HAProxy configuration file are, in order:

- The **global** section defines settings and behaviors that apply to all components of the configuration.
- The **defaults** sections define settings and behaviors that can be applied to frontends and backends as needed.
- The **frontends** sections define binds for incoming traffic and related settings and behaviors.
- The **backends** sections define application servers and related settings and behaviors.

### global

The global section appears at the top of your configuration file. It defines process-level directives such as the maximum number of connections to accept, where to store logs, and which user and group the process should run under. The example below shows just some of the available options:

```cfg
global
  maxconn 60000
  log 127.0.0.1 local0
  log 127.0.0.1 local1 notice
  user  haproxy
  group haproxy
  chroot /var/empty
```

### defaults

A defaults section stores common settings inherited by the frontend and backend sections that follow it. It can also condense long configurations by reducing duplicated lines.

By adding defaults to the configuration, you can define settings that all other sections below it will inherit when applicable. For instance, mode is applicable to both a frontend and a backend, but balance only applies to backends. Not all directives can be included in defaults; for example, the bind and server lines cannot.

```cfg
defaults
  mode http
  balance roundrobin

# Inherits mode
frontend website
  bind :80
  default_backend web_servers

# Inherits mode and balance
backend web_servers
  server s1 192.168.1.25:80
  server s2 192.168.1.26:80
```

You can define multiple defaults sections. Each one will apply to any frontend or backend that follows it, up until the next defaults section. In configurations containing multiple defaults sections, a defaults section doesn’t inherit settings from other defaults sections. Each defaults section conveys only the settings it directly specifies.

#### Override a defaults section

Each frontend and backend that follows a defaults section can still override a setting that was inherited. Building from the previous configuration sample, we have added a frontend and backend that load balance MySQL database instances. MySQL databases don’t communicate over HTTP and do better with least connections load balancing. Therefore, we override mode and balance in the mysql sections.

```cfg
defaults
  mode http
  balance roundrobin

# Inherits mode
frontend website
  bind :80
  default_backend web_servers

# Inherits mode and balance
backend web_servers
  server s1 192.168.1.25:80
  server s2 192.168.1.26:80

# Overrides mode
frontend mysql
  mode tcp
  bind :3306
  default_backend mysql_servers

# Overrides mode and balance
backend mysql_servers
  mode tcp
  balance leastconn
  server db1 192.168.1.29:3306
  server db2 192.168.1.30:3306
```

#### Define named defaults sections

You can define more than one defaults section, each with a unique name. To apply a specific, named defaults to a frontend or backend, use the from keyword to specify the desired defaults section name.

Below, the website frontend takes its default settings from the defaults section named http_defaults. The mysql frontend takes its default settings from the defaults section named tcp_defaults.

```cfg
defaults http_defaults
  mode http

defaults tcp_defaults
  mode tcp

# Inherits from http_defaults
frontend website from http_defaults
  bind :80
  default_backend web_servers

# Inherits from tcp_defaults
frontend mysql from tcp_defaults
  mode tcp
  bind :3306
  default_backend mysql_servers
```

If a frontend or backend doesn’t indicate a named defaults section using the from keyword, it takes the default values specified in the nearest preceding defaults section. Relying on section ordering in this way is not recommended because it can lead to ambiguity and slow troubleshooting.  Where possible, specify a unique name for each defaults section and use the from keyword to indicate the defaults section to use.

### Listens

A listen section serves as both a frontend, which listens to incoming traffic, and a backend, which specifies the web servers to which the load balancer sends the traffic. The following example listen section is typical because it is used for a simple TCP application. This defines the pool of upstream load balancers for a two-tier active-active high availability configuration.

```cfg
listen load_balancer_cluster
  mode tcp
  bind :80
  option tcplog
  balance roundrobin
  server lb1 192.168.1.25:80 check
  server lb2 192.168.1.26:80 check
```
