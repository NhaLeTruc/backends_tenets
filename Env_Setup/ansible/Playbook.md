# Ansible Playbook

Ansible playbooks are one of the basic components of Ansible as they record and execute Ansible’s configuration. Generally, a playbook is the primary way to automate a set of tasks that we would like to perform on a remote machine.

They help our automation efforts by gathering all the resources necessary to orchestrate ordered processes or avoid repeating manual actions. Playbooks can be reused and shared between persons, and they are designed to be human-friendly and easy to write in YAML.

## What is the difference between a playbook and a role in Ansible?

Ansible playbooks are broader in scope and capable of orchestrating multiple plays and roles across different hosts and groups, while roles are more focused components, targeting specific tasks and configurations.

When it comes to how to use them, playbooks execute the automation, while roles are used to structure and package the automation in a reusable form.

## What is the structure of an Ansible playbook?

A playbook is composed of one or more plays to run in a specific order. A play is an ordered list of tasks to run against the desired group of hosts.

Every task is associated with a module responsible for an action and its configuration parameters. Since most tasks are idempotent, we can safely rerun a playbook without any issues.

Ansible playbooks are written in YAML using the standard extension .yml with minimal syntax.

We must use spaces to align data elements that share the same hierarchy for indentation. Items that are children of other items must be indented more than their parents. There is no strict rule for the number of spaces used for indentation, but it’s pretty common to use two spaces while **Tab characters are not allowed**.

```yml
---
- name: Example Simple Playbook
  hosts: all
  become: yes

  tasks:
  - name: Copy file example_file to /tmp with permissions
    ansible.builtin.copy:
      src: ./example_file
      dest: /tmp/example_file
      mode: '0644'

  - name: Add the user 'bob' with a specific uid 
    ansible.builtin.user:
      name: bob
      state: present
      uid: 1040

- name: Update postgres servers
  hosts: databases
  become: yes

  tasks:
  - name: Ensure postgres DB is at the latest version
    ansible.builtin.yum:
      name: postgresql
      state: latest

  - name: Ensure that postgresql is started
    ansible.builtin.service:
      name: postgresql
      state: started
```

We define a descriptive name for each play according to its purpose on the top level. Then we represent the group of hosts on which the play will be executed, taken from the inventory. Finally, we define that these plays should be executed as the **root user with the become option set to yes**.

Next, we use the tasks parameter to define the list of tasks for each play. For each task, we define a clear and descriptive name. **Every task leverages a module to perform a specific operation**.

For example, the first task of the first play uses the ansible.builtin.copy module. Along with the module, we usually have to define some module arguments. For the second task of the first play, we use the module ansible.builtin.user that helps us manage user accounts. In this specific case, we configure the name of the user, the state of the user account, and its uid accordingly.

## How to write an Ansible playbook?

Writing an Ansible playbook involves creating a YAML file that specifies the hosts to configure and the tasks to perform on these hosts.

Usually, as a best practice, to specify your hosts, you need to define an Ansible inventory file.

Things to take into consideration when you are writing an Ansible playbook:

- **YAML** is sensitive to indentation, typically requiring 2 spaces for each level of indentation
- Take advantage of **variables** in your playbooks to make them more dynamic and flexible. Variables can be defined in many places, including in the playbook itself, in inventory, in separate files, or even passed at the command line
- **Use handlers** – these are special tasks that only run when notified by another task. They are typically used to restart services when configurations change.
- **Take advantage of templates** – Ansible can use Jinja2 templates to dynamically generate files based on variables
- **Use roles** – For complex setups, consider organizing your tasks into roles. This helps keep your playbooks clean and makes your tasks more reusable.

## How to run Ansible playbooks?

When we are running a playbook, Ansible executes each task in order, one at a time, for all the hosts that we selected. This default behavior could be adjusted according to different use cases using strategies.

If a task fails, Ansible stops the execution of the playbook to this specific host but continues to others that succeeded. During execution, Ansible displays some information about connection status, task names, execution status, and if any changes have been performed.

## Handling sensitive data in playbooks

At times, we would need to access sensitive data (API keys, passwords, etc.) in our playbooks. Ansible provides Ansible Vault to assist us in these cases. Storing them as variables in plaintext is considered a security risk so we can use the **ansible-vault** command to encrypt and decrypt these secrets.

After the secrets have been encrypted with a password of your choice, you can safely put them under source control in your code repositories. Ansible Vault protects only data at rest. After the secrets are decrypted, it’s our responsibility to handle them with care and not accidentally leak them.

We have the option to encrypt variables or files. Encrypted variables are decrypted on-demand only when needed, **while encrypted files are always decrypted** as Ansible doesn’t know in advance if it needs content from them.

In any case, we need to think about how are we going to manage our vault passwords. To define encrypted content, we add the **!vault** tag, which tells Ansible that the content needs to be decrypted and the **|** character before our multi-line encrypted string.

Create a new encrypted file and encrypt existing one with these commands:

```bash
ansible-vault create new_file.yml

ansible-vault encrypt existing_file.yml
```

To view and edit an encrypted file:

```bash
ansible-vault view existing_file.yml

ansible-vault edit existing_file.yml
```

To use a different password on an encrypted file, use the rekey command by using the original password. In case you need to decrypt a file, you can do so with the decrypt command:

```bash
ansible-vault rekey existing_file.yml

ansible-vault decrypt existing_file.yml
```
