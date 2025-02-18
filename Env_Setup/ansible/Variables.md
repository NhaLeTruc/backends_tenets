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
