# Ansible Modules

Modules represent distinct units of code, each one with specific functionality. Basically, they are standalone scripts written for a particular job and are used in tasks as their main functional layer.

Ansible modules are reusable, standalone scripts or programs that perform specific tasks on managed hosts or via APIs, such as managing configurations, deploying applications, or orchestrating systems. They serve as the building blocks for automation, allowing users to execute predefined actions on remote systems.

We build Ansible modules to abstract complexity and give end-users an easier way to execute their automation tasks without needing all the details. By leveraging the appropriate modules, we abstract some of the cognitive load of more complex tasks away from Ansible users.

## Ansible module example

Here’s an example of a task using the apt package manager module to install a specific version of Nginx.

```yml
- name: "Install Nginx to version {{ nginx_version }} with apt module"
   ansible.builtin.apt:
     name: "nginx={{ nginx_version }}"
     state: present
```

Modules can also be executed directly from the command line. Here’s an example of running the ping module against all the database hosts from the command line.

```bash
ansible databases -m ping
```

## How to use Ansible modules

A well-designed module provides a predictable and well-defined interface that accepts arguments that make sense and are consistent with other modules. Modules take some arguments as input and return values in JSON format after execution.

Ansible modules should follow idempotency principles, which means that consecutive runs of the same module should have the same effect if nothing else changes. Well-designed modules detect if the current and desired state match and avoid making changes if they do.

We can utilize handlers to control the flow of module and task execution in a playbook. By notifying specific handlers, modules can trigger additional downstream modules and tasks.

As mentioned, modules return data structures in JSON data. We can store these return values in variables and use them in other tasks or display them to the console. To get an idea, look at the common return values for all modules.

For custom modules, the return values should be documented along with other useful information. The command-line tool ansible-doc displays this information.

Here’s an example output of running the ansible-doc command.

```bash
ansible-doc apt
```

Many of the core modules we use extensively are part of the [Ansible.Builtin](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/index.html#plugins-in-ansible-builtin) collection. You will find other available modules in the [Collection docs](https://docs.ansible.com/ansible/latest/collections/index.html#list-of-collections).

## 11 useful and common Ansible modules

```yml
- name: Update the repository cache and update package "nginx" to latest version
  ansible.builtin.apt:
    name: nginx
    state: latest
    update_cache: yes

- name: Update the repository cache and update package "nginx" to latest version
   ansible.builtin.yum:
     name: nginx
     state: latest
     update_cache: yes

- name: Restart docker service
   ansible.builtin.service:
     name: docker
     state: restarted

- name: Create the directory "/etc/test" if it doesnt exist and set permissions
  ansible.builtin.file:
    path: /etc/test
    state: directory
    mode: '0750'

- name: Copy file with owner and permissions
  ansible.builtin.copy:
    src: /example_directory/test
    dest: /target_directory/test
    owner: joe
    group: admins
    mode: '0755'

- name: Copy and template the Nginx configuration file to the host
  ansible.builtin.template:
    src: templates/nginx.conf.j2
    dest: /etc/nginx/sites-available/default

- name: Add a line to a file if it doesnt exist
  ansible.builtin.lineinfile:
    path: /tmp/example_file
    line: "This line must exist in the file"
    state: present

- name: Add a block of config options at the end of the file if it doesn’t exist
  ansible.builtin.blockinfile:
    path: /etc/example_dictory/example.conf
    block: |
      feature1_enabled: true
      feature2_enabled: false
      feature2_enabled: true
    insertafter: EOF

- name: Run daily DB backup script at 00:00
  ansible.builtin.cron:
    name: "Run daily DB backup script at 00:00"
    minute: "0"
    hour: "0"
    job: "/usr/local/bin/db_backup_script.sh > /var/log/db_backup_script.sh.log 2>&1"

- name: Wait until a string is in the file before continuing
  ansible.builtin.wait_for:
    path: /tmp/example_file
    search_regex: "String exists, continue"

- name: Execute a script in remote shell and capture the output to file
  ansible.builtin.shell: script.sh >> script_output.log
```

## How to build custom modules in Ansible

Advanced users always have the option to develop custom modules if their needs that can’t be satisfied with existing modules. Modules always return JSON data, so they can be written in any programming language.

### Ansible modules vs. plugins

> Ansible modules are task-specific tools designed to execute actions on target hosts, such as managing files or services (e.g., the file and apt modules). By contrast, plugins extend or customize Ansible’s functionality and run on the control node. They serve various purposes, including connection management, data lookups, and output filtering.
---
> Whereas modules perform the tasks defined in playbooks, plugins enhance the execution environment and workflow management, either implicitly or through explicit configuration.

### Create a directory for your module

First, let’s create a library directory on top of our repository to place our custom module. Playbooks with a ./library directory relative to their YAML file can add custom Ansible modules that can be recognized in the Ansible module path. In this way, we can group custom modules and their related playbooks.

### Write the module code

We create our custom Python module epoch_converter.py inside the library directory. This simple module takes as input the argument epoch_timestamp and converts it to datetime type. We use another argument, state_changed, to simulate a change in the target system by this module.

ibrary/epoch_converter.py

```python
#!/usr/bin/python
 
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import datetime
 
DOCUMENTATION = r'''
---
module: epoch_converter
 
short_description: This module converts an epoch timestamp to human-readable date.
 
# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"
 
description: This module takes a string that represents a Unix epoch timestamp and displays its human-readable date equivalent.
 
options:
   epoch_timestamp:
       description: This is the string that represents a Unix epoch timestamp.
       required: true
       type: str
   state_changed:
       description: This string simulates a modification of the target's state.
       required: false
       type: bool
 
author:
   - Ioannis Moustakis (@Imoustak)
'''
 
EXAMPLES = r'''
# Convert an epoch timestamp
- name: Convert an epoch timestamp
 epoch_converter:
   epoch_timestamp: 1657382362
'''
 
RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
human_readable_date:
   description: The human-readable equivalent of the epoch timestamp input.
   type: str
   returned: always
   sample: '2022-07-09T17:59:22'
original_timestamp:
   description: The original epoch timestamp input.
   type: str
   returned: always
   sample: '16573823622'
 
'''
 
from ansible.module_utils.basic import AnsibleModule
 
 
def run_module():
   # define available arguments/parameters a user can pass to the module
   module_args = dict(
       epoch_timestamp=dict(type='str', required=True),
       state_changed=dict(type='bool', required=False)
   )
 
   # seed the result dict in the object
   # we primarily care about changed and state
   # changed is if this module effectively modified the target
   # state will include any data that you want your module to pass back
   # for consumption, for example, in a subsequent task
   result = dict(
       changed=False,
       human_readable_date='',
       original_timestamp=''
   )
 
   # the AnsibleModule object will be our abstraction working with Ansible
   # this includes instantiation, a couple of common attr would be the
   # args/params passed to the execution, as well as if the module
   # supports check mode
   module = AnsibleModule(
       argument_spec=module_args,
       supports_check_mode=True
   )
 
   # if the user is working with this module in only check mode we do not
   # want to make any changes to the environment, just return the current
   # state with no modifications
   if module.check_mode:
       module.exit_json(**result)
 
   # manipulate or modify the state as needed (this is going to be the
   # part where your module will do what it needs to do)
   result['original_timestamp'] = module.params['epoch_timestamp']
   result['human_readable_date'] = datetime.datetime.fromtimestamp(int(module.params['epoch_timestamp']))
 
   # use whatever logic you need to determine whether or not this module
   # made any modifications to your target
   if module.params['state_changed']:
       result['changed'] = True
 
   # during the execution of the module, if there is an exception or a
   # conditional state that effectively causes a failure, run
   # AnsibleModule.fail_json() to pass in the message and the result
   if module.params['epoch_timestamp'] == 'fail':
       module.fail_json(msg='You requested this to fail', **result)
 
   # in the event of a successful module execution, you will want to
   # simple AnsibleModule.exit_json(), passing the key/value results
   module.exit_json(**result)
 
 
def main():
   run_module()
 
 
if __name__ == '__main__':
   main()
```

### Test your module

To test our module, let’s create a test_custom_module.yml playbook in the same directory as our library directory.

test_custom_module.yml

```yml
- name: Test my new module
  hosts: localhost
  tasks:
  - name: Run the new module
    epoch_converter:
      epoch_timestamp: '1657382362'
      state_changed: yes
    register: show_output
  - name: Show Output
    debug:
      msg: '{{ show_output }}'
```
