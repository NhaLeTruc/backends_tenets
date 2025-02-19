# Ansible Playbook Advanced Usages

## How to run multiple playbooks in Ansible

Running multiple playbooks in Ansible can be achieved in several ways:

- Using **sequential execution** – You can run the playbooks one by one or use the && operator

```bash
ansible-playbook -i inventory.ini playbook1.yaml && ansible-playbook -i inventory.ini playbook2.yaml
```

- Using a **master playbook** – Includes multiple other playbooks using the import_playbook directive

```yml
---
- import_playbook: playbook1.yaml
- import_playbook: playbook2.yaml
```

- **Ansible Tower or AWX** – you can use one of these tools to provide workflows that allow you to string together multiple playbooks.
- **Ansible runner** – used to execute multiple playbooks programmatically, manage their execution environment, and also handle the outputs and logs.
- **Makefile** – you could potentially take advantage of Makefile to organize and run Ansible playbooks.

## Using conditional tasks in playbooks

To further control execution flow in Ansible, we can leverage conditionals. Conditionals allow us to run or skip tasks based on if certain conditions are met. Variables, facts, or results of previous tasks along with operators, can be used to create such conditions.

ome examples of use cases could be to update a variable based on a value of another variable, skip a task if a variable has a specific value, execute a task only if a fact from the host returns a value higher than a threshold.

To apply a simple conditional statement, we use the Ansible when parameter on a task. If the condition is met, the task is executed. Otherwise, it is skipped.

```yml
- name: Example Simple Conditional
  hosts: all
  vars:
    trigger_task: true

  tasks:
  - name: Install nginx
    apt:
      name: "nginx"
      state: present
    when: trigger_task
```

In the above example, the task is executed since the condition is met.

Another common pattern is to control task execution based on attributes of the remote host that we can obtain from **facts**.

```yml
- name: Example Facts Conditionals 
  hosts: all
  vars:
    supported_os:
      - RedHat
      - Fedora

  tasks:
  - name: Install nginx
    yum:
      name: "nginx"
      state: present
    when: ansible_facts['distribution'] in supported_os
```

It’s possible to combine **multiple conditions with logical operators** and group them with parenthesis. When statement also supports using a list in cases when we have multiple conditions that all need to be true:

```yml
when: (colour=="green" or colour=="red") and (size="small" or size="medium")

when:
  - ansible_facts['distribution'] == "Ubuntu"
  - ansible_facts['distribution_version'] == "20.04"
  - ansible_facts['distribution_release'] == "bionic"
```

Another option is to use **conditions based on registered variables** that we have defined in previous tasks:

```yml
- name: Example Registered Variables Conditionals
  hosts: all

  tasks:
  - name: Register an example variable
    ansible.builtin.shell: cat /etc/hosts
    register: hosts_contents

  - name: Check if hosts file contains "localhost"
    ansible.builtin.shell: echo "/etc/hosts contains localhost"
    when: hosts_contents.stdout.find(localhost) != -1
```

## How to use loops in Ansible playbooks

Ansible allows us to iterate over a set of items in a task to execute it multiple times with different parameters without rewriting it. For example, to create several files, we would use a task that iterates over a list of directory names instead of writing five tasks with the same module.

To iterate over a simple list of items, use the loop keyword. We can reference the current value with the loop variable/dictionary items.

```yml
- name: "Create some files"
  ansible.builtin.file:
    state: touch
    path: /tmp/{{ item }}
  loop:
    - example_file1
    - example_file2
    - example_file3

- name: "Create some files with dictionaries"
  ansible.builtin.file:
    state: touch
    path: "/tmp/{{ item.filename }}"
    mode: "{{ item.mode }}"
  loop:
    - { filename: 'example_file1', mode: '755'}
    - { filename: 'example_file2', mode: '775'}
    - { filename: 'example_file3', mode: '777'}

- name: Show all the hosts in the inventory
  ansible.builtin.debug:
    msg: "{{ item }}"
  loop: "{{ groups['databases'] }}"
```

By combining conditionals and loops, we can select to execute the task only on some items in the list and skip it for others:

```yml
- name: Execute when values in list are lower than 10
  ansible.builtin.command: echo {{ item }}
  loop: [ 100, 200, 3, 600, 7, 11 ]
  when: item < 10
```

Finally, another option is to use the keyword **until** to retry a task until a condition is true.

```yml
- name: Retry a task until we find the word "success" in the logs
  shell: cat /var/log/example_log
  register: logoutput
  until: logoutput.stdout.find("success") != -1
  retries: 10
  delay: 15
```

In the above example, we check the file example_log 10 times, with a delay of 15 seconds between each check until we find the word success. If we let the task run and add the word success to the example_log file after a while, we notice that the task stops successfully.

## How to loop a block in Ansible

Neither **loops** nor **with_items** can be used with blocks in Ansible. Alternatively, you could use **include_tasks** to achieve a similar result and include task files based on specified conditions.

## How to use multiple loops in Ansible? (Nested loops)

You can use multiple loops in Ansible by nesting loops within each other. Nested loops are loops within loops that allow you to iterate over complex data structures and perform multiple iterations within a single task. They can be useful if you need to deploy multiple applications across different environments, set up multiple services with distinct configurations, or manage permissions for multiple users.

```yml
- name: Display applications for each environments
  hosts: localhost
  vars:
    apps_environments:
      - app: webapp
        environments:
          - env: development
            url: dev.example.com
          - env: production
            url: example.com
      - app: api
        environments:
          - env: development
            url: dev.api.example.com
          - env: production
            url: api.example.com
  tasks:
    - name: Display application for each environment
      debug:
        msg: "Displaying {{ item.0.app }} for {{ item.1.env }} environment with URL {{ item.1.url }"
      loop: "{{ query('subelements', apps_environments, 'environments') }}"
```

## Ansible loop control

You can use many different options to manage and customize the flow of your Ansible loops.

The key features of the loop_control keyword include:

- **pause** — This option allows you to pause your loop for a specific time (in seconds) between each iteration. For example, it can be useful when you need to place a timer after the first iteration to the next iteration due to interacting with specific APIs that have rate limits.
- **index_var** — The index_var option lets you access the index of the current loop that is running, which might be helpful when you need to access the position of the current item in the loop.
- **loop_var** — This option allows you to customize the ‘item’ variable name used in the loop. You can use this to improve the readability of your playbook by specifying a familiar and descriptive name.
- **extended** — The extended option was added in Ansible version 2.8. Using this option, you can pull additional details of the loop (e.g., the current item’s index and the total number of items), which is helpful for debugging.

```yml
---
- name: Loop Control Pause
  hosts: myhosts
  tasks:
    - name: Echo items with a pause
      command: echo "{{ item }}"
      loop:
        - "Item 1"
        - "Item 2"
        - "Item 3"
      loop_control:
        pause: 5 
```

Here is another example of using the pause and loop_var feature of loop_control to perform a REST API call to a service that limits the number of requests you can make per minute:

```yml
---
- name: API calls
  hosts: localhost
  tasks:
    - name: Call the API with a 2 second delay between requests
      uri:
        url: "https://my_example.com/api/{{ item.endpoint }}"
        method: GET
        return_content: yes
        headers:
          Authorization: "Bearer YOUR_API_TOKEN"
      loop:
        - { endpoint: 'users', id: 1 }
        - { endpoint: 'users', id: 2 }
        - { endpoint: 'posts', id: 1 }
      loop_control:
        loop_var: item
        pause: 2
      register: api_response

    - name: Display API response
      debug:
        msg: "API response for {{ item.item.endpoint }} ID {{ item.item.id }}: {{ item.json }}"
      loop: "{{ api_response.results }}"
      loop_control:
        label: "{{ item.item.endpoint }} ID {{ item.item.id }}"
```
