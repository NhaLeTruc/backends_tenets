# Ansible Inventory File

Full guide [here](https://spacelift.io/blog/ansible-inventory) and [here](https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html) and [Develop custom dynamic inventory](https://docs.ansible.com/ansible/latest/dev_guide/developing_inventory.html#developing-inventory)

## What is an Ansible inventory file?

An Ansible inventory is a collection of managed hosts we want to manage with Ansible for various automation and configuration management tasks. Typically, when starting with Ansible, we define a static list of hosts known as the inventory. These hosts can be grouped into different categories, and then we can leverage various patterns to run our playbooks selectively against a subset of hosts.

By default, the inventory is stored in **/etc/ansible/hosts**, but you can specify a different location with the **-i** flag or the **ansible.cfg** configuration file.

## Ansible inventory basics

```cfg
[webservers]
host01.mycompany.com
host02.mycompany.com

[databases]
host03.mycompany.com
host04.mycompany.com
```

In this example, we use the INI format, define four managed hosts, and group them into two host groups; webservers and databases. The group names can be specified between brackets, as shown above.

Inventory groups are one of the handiest ways to control Ansible execution. Hosts can also be part of multiple groups.

```cfg
[webservers]
host01.mycompany.com 
host02.mycompany.com

[databases]
host03.mycompany.com
host04.mycompany.com

[europe]
host01.mycompany.com
host03.mycompany.com

[asia]
host02.mycompany.com
host04.mycompany.com
```

> Note: By default, we can also reference two groups without defining them. The all group targets all our hosts in the inventory, and the ungrouped contains any host that isn’t part of any user-defined group.

We can also create nested groups of hosts if necessary.

```cfg
[paris]
host01.mycompany.com
host02.mycompany.com

[amsterdam]
host03.mycompany.com
host04.mycompany.com

[europe:children]
paris
amsterdam
```

To list a range of hosts with similar patterns, you can leverage the range functionality instead of defining them one by one. For example, to define ten hosts (host01, host02, …. host10):

```cfg
databases
hosts[01:10].mycompany.com
```

Another useful functionality is the option to define aliases for hosts in the inventory. For example, we can run Ansible against the host alias host01 if we define it in the inventory as:

```cfg
host01 ansible_host=host01.mycompany.com
```

A typical pattern for inventory setups is separating inventory files per environment. Find below an example of keeping separate staging and production inventories.

## Ansible inventory variables

An important aspect of Ansible’s project setup is variable assignment and management. Ansible offers many different ways of setting variables and defining them in the inventory is one of them.

For example, let’s define one variable for a different application version for every host in our dummy inventory from before.

```cfg
[webservers]
host01.mycompany.com app_version=1.0.1
host02.mycompany.com app_version=1.0.2

[databases]
host03.mycompany.com app_version=1.0.3
host04.mycompany.com app_version=1.0.4
```

Ansible-specific connection variables such as **ansible_user** or **ansible_host** are examples of host variables defined in the inventory.

Although setting variables in the inventory is possible, it’s usually not the preferred way. Instead, store separate host and group variable files to enable better organization and clarity for your Ansible projects. Note that host and group variable files must use the YAML syntax.

> In the same directory where we keep our inventory file, we can create two folders named group_vars and host_vars containing our variable files.

## Multiple Ansible inventory sources

We have the option to combine different inventories and sources, such as directories, dynamic inventory scripts, or inventory plugins during runtime or in the configuration. This becomes especially useful in cases where we want to target multiple environments or otherwise isolated setups.

```bash
ansible-playbook apply_updates.yml -i development -i testing -i staging -i production
```

## What are Ansible dynamic inventories?

Many modern environments are dynamic, cloud-based, possibly spread across multiple providers, and constantly changing. In these cases, maintaining a static list of managed nodes is time-consuming, manual, and error-prone.

> Ansible’s dynamic inventory feature allows Ansible to automatically generate the list of hosts or nodes in the infrastructure rather than relying on a static inventory file. This is especially useful in dynamic and cloud-based environments where servers may be created, modified, or removed frequently.

Ansible has two methods for properly tracking and targeting a dynamic set of hosts: **inventory plugins** and **inventory scripts**. The official suggestion is to prefer inventory plugins that benefit from the recent updates to Ansible core.

To see a list of available inventory plugins you can leverage to build dynamic inventories, you can execute **ansible-doc -t inventory -l**. We will look at one of them, the amazon.aws.aws_ec2, to get hosts from Amazon Web Services EC2.

For plugin-specific docs and examples, use the command ansible-doc -t inventory amazon.aws.aws_ec2. Install the Ansible Galaxy collection amazon.aws to work with the plugin by running ansible-galaxy collection install **amazon.aws**.

## Ansible dynamic inventory AWS example

dynamic_inventory_aws_ec2.yml

```yml
plugin: amazon.aws.aws_ec2
regions:
  - us-east-1
  - us-east-2
  - us-west-2
 
hostnames: tag:Name
keyed_groups:
  - key: placement.region
    prefix: aws_region
  - key: tags['environment']
    prefix: env
  - key: tags['role']
    prefix: role
groups:
   # add hosts to the "private_only" group if the host doesn't have a public IP associated to it
  private_only: "public_ip_address is not defined"
compose:
  # use a private address where a public one isn't assigned
  ansible_host: public_ip_address|default(private_ip_address)
```

Let’s view the generated inventory with the command:

```bash
ansible-inventory -i dynamic_inventory_aws_ec2.yml --graph
```

The plugin fetches information from our AWS account and creates several groups according to our configuration and options.

To persist the inventory to a file, you can use this command:

```bash
ansible-inventory -i dynamic_inventory_aws_ec2.yml --list --output inventory/dynamic_inventory_aws_ec2 -y
```
