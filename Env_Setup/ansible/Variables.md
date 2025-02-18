# Ansible Variables

Full guide is [here](https://spacelift.io/blog/ansible-variables)

Ansible variables are dynamic values used within Ansible playbooks and roles to enable customization, flexibility, and reusability of configurations. They are very similar to variables in programming languages, helping you manage complex tasks more efficiently by allowing the same playbook or role to be applied across different environments, systems, or contexts without the need for hardcoding specific information.

## Variable naming rules

Ansible has a strict set of rules to create valid variable names. Variable names can contain only letters, numbers, and underscores and must start with a letter or underscore. Some strings are reserved for other purposes and aren’t valid variable names, such as Python Keywords or Playbook Keywords.

## Types of variables in Ansible

Variables in Ansible can come from different sources and can be used in playbooks, roles, inventory files, and even within modules. 

Here are the variable types you may encounter while using Ansible:

- **Playbook** variables – These variables are used to pass values into playbooks and roles and can be defined inline in playbooks or included in external files.
- **Task** variables – These variables are specific to individual tasks within a playbook. These can override other variable types for the scope of the task in which they are defined.
- **Host** variables – Specific to hosts, these variables are defined in the inventory or loaded from external files or scripts and can be used to set attributes that differ between hosts.
- **Group** variables – Similar to host variables but used for a group of hosts and are defined in the inventory or separate files in the group_vars directory.
- **Inventory** variables – These variables are defined in the inventory file itself and can be applied at different levels (host, group, all groups).
- **Fact** variables – Gathered by Ansible from the target machines, facts are a rich set of variables (including IP addresses, operating system, disk space, etc.) that represent the current state of the system and are automatically discovered by Ansible.
- **Role** variables – Defined within a role, these variables are usually part of the role’s default variables (defaults/main.yaml file) or variables intended to be set by the role user (vars/main.yaml file) and are used to enable reusable and configurable roles.
- **Extra** variables – Passed to Ansible at runtime using the -e or –extra-vars command-line option. They have the highest precedence and can be used to override other variables or to pass data that might change between executions.
- **Magic** variables – Special variables such as hostvars, group_names, groups, inventory_hostname, and ansible_playbook_python, provide information about the execution context and allow access to inventory data programmatically.
- **Environment** variables –  Used within Ansible playbooks to access environment variables from the system running the playbook or from remote systems.

## Simple variables

```yml
- name: Example Simple Variable
  hosts: all
  become: yes
  vars:
    username: bob

  tasks:
  - name: Add the user {{ username }}
    ansible.builtin.user:
      name: "{{ username }}"
      state: present
```

In the above example, after the vars block, we define the variable username, and assign the value bob. Later, to reference the value in the task, we use Jinja2 syntax like this "{{ username }}"

If a variable’s value starts with curly braces, we must quote the whole expression to allow YAML to interpret the syntax correctly.

## List, dictionary & nested variables

```yml
vars:
  version:
    - v1
    - v2
    - v3

version: "{{ version[2] }}"
```

Another useful option is to store key-value pairs in variables as dictionaries. For example:

```yml
vars:
  users: 
    - user_1: maria
    - user_2: peter
    - user_3: sophie
```

Similarly, to reference the third field from the dictionary, use the bracket or dot notation:

```yml
users['user_3']
users.user_3
```

Sometimes, we have to create or use nested variable structures. For example, facts are nested data structures. We have to use a bracket or dot notation to reference nested variables.

```yml
vars:
  cidr_blocks:
      production:
        vpc_cidr: "172.31.0.0/16"
      staging:
        vpc_cidr: "10.0.0.0/24"

tasks:
- name: Print production vpc_cidr
  ansible.builtin.debug:
    var: cidr_blocks['production']['vpc_cidr']
```

## Special variables

Ansible special variables are a set of predefined variables that contain information about the system data, inventory, or execution context inside an Ansible playbook or role. These include magic variables, connection variables, and facts. The names of these variables are reserved.

### Magic variables

Magic variables are automatically created by Ansible and cannot be changed by a user. These variables will always reflect the internal state of Ansible, so they can be used only as they are.

```yml
---
- name: Echo playbook
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Echo inventory_hostname
      ansible.builtin.debug:
        msg:
          - "Hello from Ansible playbook!"
          - "This is running on {{ inventory_hostname }}"
```

In the above playbook, we are defining a playbook that uses the inventory_hostname magic variable. We are using this variable to get the name of the host on which Ansible runs and print a message with it as shown below.

Apart from inventory_hostname, some other essential magic variables are:

- **hostvars** → leveraged for getting information about other hosts in the inventory, including any variables that are associated with them.
- **play_hosts** → lists all the hosts that are targeted by the current play.
- **group_names** → contains a list of groups names to which the current host belongs in the inventory.
- **groups** → key/value pair of all the groups in the inventory with all the hosts that belong to each group.

### Connection variables

Connection variables are used to define how the machine that runs Ansible connects to remote hosts during the execution of tasks and playbooks. These variables provide flexibility in managing various connection types, authentication methods, and host-specific configurations.

### Registering variables

During our plays, we might find it handy to utilize the output of a task as a variable that we can use in the following tasks. We can use the keyword register to create our own custom variables from task output.

### Environment variables

Environment variables are a powerful way to influence the behavior of playbooks and tasks by passing external values into the Ansible runtime environment. These can be system environment variables available where Ansible is executed or on the managed nodes.

You should be cautious when using environment variables for sensitive data, as their values might be logged or exposed in debugging output, and relying on them will affect the overall portability and reusability of your playbook. Setting environment variables within tasks or plays will override those of the same name in the system environment for the duration of the task or play execution.

## Variable scope

Ansible provides many options on setting variables, and the ultimate decision on where to set them lies with us based on the scope we would like them to have. Conceptually, there are three main options available for scoping variables. 

First, we have the global scope where the values are set for all hosts. This can be defined by the Ansible configuration, environment variables, and command line. 

We set values for a particular host or group of hosts using the host scope. For example, there is an option to define some variables per host in the inventory file.

Lastly, we have the play scope, where values are set for all hosts in the context of a play. An example would be the vars section we have seen in previous examples in each playbook.

## Where to set Ansible variables?

Variables can be defined with Ansible in many different places. There are options to set variables in playbooks, roles, inventory, var files, and command line.

### Vars block

```yml
- name: Set variables in a play
  hosts: all
  vars:
    version: 12.7.1
```

### Inventory files

```cfg
[webservers]
webserver1 ansible_host=10.0.0.1 ansible_user=user1
webserver2 ansible_host=10.0.0.2 ansible_user=user2

[webservers:vars]
http_port=80
```

To better organize our variables, we could gather them in separate host and group variables files. In the same directory where we keep our Ansible inventory or playbook files, we can create two folders named group_vars and host_vars that would contain our variable files. For example:

- group_vars/databases
- group_vars/webservers
- host_vars/host1
- host_vars/host2

### Custom var files

Variables can also be set in custom var files. Let’s check an example that uses variables from an external file and the group_vars and host_vars directories.

```yml
- name: Example External Variables file
  hosts: all
  vars_files:
    - ./vars/variables.yml

  tasks:
  - name: Print the value of variable docker_version
    debug: 
      msg: "{{ docker_version}} "
  
  - name: Print the value of group variable http_port
    debug: 
      msg: "{{ http_port}} "
  
  - name: Print the value of host variable app_version
    debug: 
      msg: "{{ app_version}} "
```

The vars/variables.yml file:

```yml
docker_version: 20.10.12
```

The group_vars/webservers file:

```yml
http_port: 80
ansible_host: 127.0.0.1
ansible_user: vagrant
```

The host_vars/host1 file

```yml
app_version: 1.0.1
ansible_port: 2222
ansible_ssh_private_key_file: ./.vagrant/machines/host1/virtualbox/private_key
```

The host_vars/host2 file:

```yml
app_version: 1.0.2
ansible_port: 2200
ansible_ssh_private_key_file: ./.vagrant/machines/host2/virtualbox/private_key
```

## Variables precedence

Since variables can be set in multiple places, Ansible applies variable precedence to select the variable value according to some hierarchy. The general rule is that variables defined with a more explicit scope have higher priority.

For example, role defaults are overridden by mostly every other option. Variables are also flattened to each host before each play, so all group and hosts variables are merged. Host variables have higher priority than group variables. 

Explicit variable definitions like the vars directory or an include_vars task override variables from the inventory. Finally, extra vars defined at runtime always win precedence. For a complete list of options and their hierarchy, look at the official documentation [here](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_variables.html#understanding-variable-precedence)
