# Ansible Handlers

Ansible is a configuration management tool that helps maintain software configurations across infrastructure components. It uses an agent-less architecture to manage these changes.

At the core of any Ansible project, playbooks outline a series of steps needed to ensure the desired state of software applications and libraries for business services. These playbooks are written in YAML files, which Ansible executes sequentially by connecting to target systems via SSH.

**Sometimes you need certain steps in a playbook to run conditionally**, such as restarting a server only when configuration files change. By default, Ansible will run these steps regardless of changes, which may not always be desirable.

Ansible addresses this with handlers, which enable conditional execution of specific tasks, ensuring that configuration changes only trigger necessary actions. They are essential for adding flexibility and responsiveness to Ansible playbooks.

## What are Ansible handlers?

Handlers are a special type of task in Ansible that helps manage tasks that need to occur conditionally in Ansible playbooks. They don’t run unless ‘notified’ by other tasks in the sequence, for example, restarting a service after a configuration file has been modified.

Handlers differ from regular tasks in a couple of ways. First, they are not part of the sequential execution and are **only executed towards the end of the playbook if notified**.

Furthermore, when you trigger multiple handlers, **they execute only once during the run**. This ensures that these special operations are performed efficiently, without repetition, resulting in more streamlined and predictable playbook execution.

## Ansible handlers structure

Handlers are declared using the handler keyword in the Ansible playbook YAMLs. Other than that, they retain the same syntax for the individual tasks.

**Handlers are triggered by tasks using the notify or listen attribute** and are executed in the order they are defined in the handlers section. They are **executed after all tasks are completed** and **only if a task has notified them** during the play. The handler won’t run if a task that notifies a handler fails and the failure isn’t ignored.

If multiple tasks notify different handlers, Ansible collects all the notified handlers and **executes them in the order they are defined in the handlers section**, regardless of the order in which they were notified during the task execution. If a handler is notified multiple times during a play, it will still **only run once at the end of the play**.

## How to use a single Ansible handler

To use a single Ansible handler, define the handler in the handlers section and notify it from tasks using the notify or listen attribute.

The example below notifies the Start Apache handler after installing the Apache server on the nodes. If the Apache server is already present on the node, the Start Apache handler will not be called.

```yml
---
- name: Example Ansible playbook
  hosts: all
  become: yes
  tasks:
    - name: Install Apache
      apt:
        name: apache2
        state: present
      notify: Start Apache

    # other regular tasks…

  handlers:          # handlers
    - name: Start Apache
      shell: /usr/sbin/apache2ctl start
      args:
        creates: /var/run/apache2/apache2.pid

    - name: Reload Apache
      shell: /usr/sbin/apache2ctl -k graceful
      args:
        creates: /var/run/apache2/apache2.pid
```

In the example above, we used the notify attribute to notify the corresponding handler by its name. When the task is executed, it notifies the handler to execute its configuration. If not, the handler is not executed.

The same behavior can be achieved using the listen attribute on handlers, as shown in the example below.

```yml
---
- name: Single handler demo
  hosts: all
  become: yes
  tasks:
    - name: Example task
      apt:
        name: package_name
        state: present
      notify: "example task event"

  handlers:
    - name: Handler 1
      shell: <command>
      args:
        creates: /test/test1.txt
      listen: "example task event"
```

In the playbook configuration above, when the Example task is executed, it notifies the handlers using the generic string example task event. Handler 1 then listens to this event and executes the code.

Using the listen keyword decouples the dependency on the handler’s name and is a recommended approach starting with Ansible 2.2.

## How to trigger multiple handlers

In certain situations, you may need to execute more than one handler. For multiple Ansible handlers, define each handler in the handlers section, specifying unique names for each, and use notify or listen to trigger them from tasks. Multiple handlers can be notified from a single task, and they will run in the order they are defined if triggered by the same play.

The example below shows how to notify multiple handlers by their names from the task:

```yml
---
- name: Single handler demo
  hosts: all
  become: yes
  tasks:
    - name: Example task
      apt:
        name: package_name
        state: present
      notify:
        - Handler 1
        - Handler 2

  handlers:
    - name: Handler 1
      shell: <command>
      args:
        creates: /test/test1.txt

    - name: Handler 2
      shell: <command>
      args:
        creates: /test/test2.txt
```
