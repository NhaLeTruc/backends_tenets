# Ansible Blocks

## What are blocks in Ansible?

Ansible blocks are a way to **logically group and split tasks in Ansible playbooks**. By grouping multiple tasks together using blocks, you can apply common attributes, error handling, or conditional statements and can set data or directives to various tasks simultaneously.

When to use Ansible blocks:

- Organization – Blocks help with playbook organization and ensure code duplication and standard behavior across tasks.
- Conditional execution – Attributes or directives set at the Ansible block level aren’t applied directly to the block itself but are inherited by and applied to each task in the block. Examples include conditionals such as when, block variables, or privilege escalation such as become.
- Debugging – Blocks also help with error handling with the rescue keyword. You can define a rescue section to run specific tasks when an error occurs within the block.
- Error recovery – Another handy use case is cleanup situations using the always keyword to execute generic tasks regardless of what happens inside the main block of tasks.

## How to use blocks in Ansible playbooks?

Here’s an example of how to define an Ansible block and apply some common attributes to the block’s tasks:

```yml
 tasks:
    - name: The code below defines an example Ansible Block
      block:
        - name: Install Apache
          ansible.builtin.yum:
            name: httpd
            state: present

        - name: Start Apache service
          ansible.builtin.service:
            name: httpd
            state: started 
      rescue:
        - name: Task to run if there is an error
          ansible.builtin.command: echo "Error occurred"
      always:
        - name: Task that always runs
          ansible.builtin.command: echo "This always runs"
```

- block: Contains a list of tasks that are grouped together. All tasks inside the block will be executed in sequence.
- rescue: If any task within the block fails, the tasks inside rescue will be executed to handle the failure. (Optional)
- always: Tasks inside always are executed no matter whether the block or rescue sections succeeded or failed. It can be used for cleanup or logging purposes. (Optional)

More usages details could be found [here](https://spacelift.io/blog/ansible-block)
