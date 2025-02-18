# Ansible Tags

Ansible tags provide users with granular control over the execution of specific tasks, roles, and even entire plays within a playbook. Tags are specified in the Playbook YAML file and assigned to a task or role. When using the –tags parameter in the ansible-playbook command, Ansible will execute the tagged tasks only and ignore the rest. This feature is particularly useful when you want to avoid running the entire playbook and focus instead on specific components to prevent potential disruptions in your environment.

## Benefits of using Ansible tags

With tags, you can easily debug your Ansible playbook when something isn’t working properly. Placing a tag on the task you want to test and running the tagged items via the command line can help you get to the root cause without running the entire playbook. Playbooks can easily become complex, so selective execution can save time and resources.

Ansible tags are also very flexible because you can tag certain tasks or roles and do the opposite of running them. You can skip specific tasks you believe might be problematic to run at the time of execution.

Tags can also help you reuse certain components from your playbook across different scenarios, making them a powerful tool if used correctly.

## Adding a tag to a task

In the following example, we are tagging tasks in our playbook. These tasks are responsible for installing Apache and starting the Apache service:

```yml
---
- name: Apache
  hosts: test
  tasks:
    - name: Install Apache
      apt:
        name: apache2
        state: present
      tags: install_apache

    - name: Start Apache Service
      service:
        name: apache2
        state: started
      tags: start_service
```

With the following command, we can trigger only the Install Apache tagged task: 

```bash
ansible-playbook playbook.yml --tags "install_apache"
```

## How to list all tags in Ansible?

```bash
ansible-playbook apache-playbook.yml --list-tags
```

## Using multiple tags in Ansible

```yml
---
- name: MyWebApp
  hosts: test
  tasks:
    - name: Install Apache
      apt:
        name: apache2
        state: present
      tags:
        - install
        - webserver

    - name: Install MySQL
      apt:
        name: mysql-server
        state: present
      tags:
        - install
        - database

    - name: Configure Apache
      template:
        src: apache.conf.j2
        dest: /etc/apache2/apache2.conf
      tags:
        - configure
        - webserver
```

Now, we can deploy the Apache web server without worrying about touching the database and vice versa. We have the flexibility to run the following commands for different scenarios:

```bash
ansible-playbook myapp.yml --tags "install"

ansible-playbook myapp.yml --tags "webserver"

ansible-playbook myapp.yml --tags "database"
```

We can also call multiple tags in the Ansible command:

```bash
ansible-playbook example_playbook.yml --skip-tags "configure"
```

## The Always and Never tags

Two special Ansible tags ensure consistency and stability in your playbook:

- The **always** tag guarantees the task will run regardless of what tag is passed in from the command line. This is useful when critical validation steps, environment setup tasks, or cleanup operation tasks need to run constantly.
- The **never** tag does the opposite. It ensures that tasks will not run regardless of which tag is being passed down. This is useful for tasks that are being deprecated and should not be run anymore. You can also use the **never** tag if you want to temporarily disable certain tasks during testing or debugging.

## Using tags on variables

You can pass in tag values through variables, which allows you to manage all your tags from a single point instead of having them spread out across the playbook.

```yml
---
- name: Playbook with Tags and Variables
  hosts: all
  vars:
    install_tag: "install_apache"

  tasks:
    - name: Install Apache
      apt:
        name: apache2
        state: present
      tags: "{{ install_tag }}"
```

## Ansible tags on facts

Ansible Facts are system properties that Ansible gathers from managed nodes when Ansible connects to them. These properties include details about the OS, installed packages, network interfaces, and more. By default, gathering facts runs at the beginning of each playbook run.

Sometimes, running gather_facts every time the playbook runs can be time-consuming and affect the playbook’s performance. With tags, you have more control over the flow of execution, allowing you to collect data only when a certain tag is specified.

In the following example, we want only a few tasks to run if gather_facts tag is used and the rest of the tasks to run as usual (Note: gather_facts is specifically set to false since, by default, gather_facts is set to true).

To use tags to gather Facts, you will need to use the setup module:

```yml
---
- name: Gathering facts with tags
  hosts: all
  gather_facts: false
  tasks:
    - name: Gather facts
      setup:
      tags: gather_facts

    - name: Install Apache on Ubuntu
      apt:
        name: apache2
        state: present
      when: ansible_facts['os_family'] == "Debian"
      tags:
        - install_apache

    - name: Install Apache on CentOS
      yum:
        name: httpd
        state: present
      when: ansible_facts['os_family'] == "RedHat"
      tags:
        - install_apache

    - name: Configure Apache on Ubuntu
      template:
        src: apache_ubuntu.conf.j2
        dest: /etc/apache2/apache2.conf
      when: ansible_facts['os_family'] == "Debian"
      tags:
        - configure_apache

    - name: Configure Apache on CentOS
      template:
        src: apache_centos.conf.j2
        dest: /etc/httpd/conf/httpd.conf
      when: ansible_facts['os_family'] == "RedHat"
      tags:
        - configure_apache

    - name: Create a directory
      file:
        path: /tmp/myapp
        state: directory

    - name: Copy application files
      copy:
        src: /local/path/
        dest: /tmp/myapp/
```

Now, if we want to install Apache on a Debian machine, we can use the following command:

```bash
ansible-playbook apache.yml --tags "gather_facts,install_apache"
```

## Using Tags IRL

Detailed examples could be found [here](https://spacelift.io/blog/ansible-tags)
