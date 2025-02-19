# Ansible Facts and Magic variables

With Ansible you can retrieve or discover certain variables containing information about your remote systems or about Ansible itself. Variables related to remote systems are called facts. With facts, you can use the behavior or state of one system as a configuration on other systems. For example, you can use the IP address of one system as a configuration value on another system. Variables related to Ansible are called magic variables.

## Ansible facts

Ansible facts are leveraged for getting system and hardware facts gathered about the current host during playbook execution. This data is often utilized for creating dynamic inventories, templating, or making decisions based on host-specific attributes. The gathered facts can be accessed using the ansible_facts variable, allowing you to reference specific information like the operating system, IP address, or CPU architecture.

To collect facts about a specific host, you can run the following command:

```bash
ansible -m setup <hostname>
```

Ansible facts are data related to your remote systems, including operating systems, IP addresses, attached filesystems, and more. You can access this data in the ansible_facts variable. By default, you can also access some Ansible facts as top-level variables with the ansible_ prefix. You can disable this behavior using the INJECT_FACTS_AS_VARS setting. To see all available facts, add this task to a play:

```yml
- name: Print all available facts
  ansible.builtin.debug:
    var: ansible_facts
```

or

```bash
ansible <hostname> -m ansible.builtin.setup
```

You can reference the model of the first disk in the facts shown above in a template or playbook as:

```yml
{{ ansible_facts['devices']['xvda']['model'] }}
```

## Caching facts

Like registered variables, facts are stored in memory by default. However, unlike registered variables, facts can be gathered independently and cached for repeated use. With cached facts, you can refer to facts from one system when configuring a second system, even if Ansible executes the current play on the second system first. For example:

```yml
{{ hostvars['asdf.example.com']['ansible_facts']['os_family'] }}
```

Caching is controlled by the cache plugins. By default, Ansible uses the memory cache plugin, which stores facts in memory for the duration of the current playbook run. To retain Ansible facts for repeated use, select a different cache plugin. See Cache plugins for details.

Fact caching can improve performance. If you manage thousands of hosts, you can configure fact caching to run nightly, and then manage configuration on a smaller set of servers periodically throughout the day. With cached facts, you have access to variables and information about all hosts even when you are only managing a small number of servers.

## Disabling facts

By default, Ansible gathers facts at the beginning of each play. If you do not need to gather facts (for example, if you know everything about your systems centrally), you can turn off fact gathering at the play level to improve scalability. Disabling facts may particularly improve performance in push mode with very large numbers of systems, or if you are using Ansible on experimental platforms. To disable fact gathering:

```yml
- hosts: whatever
  gather_facts: false
```

## Adding custom facts

The setup module in Ansible automatically discovers a standard set of facts about each host. If you want to add custom values to your facts, you can write a custom facts module, set temporary facts with a *ansible.builtin.set_fact* task, or provide permanent custom facts using the *facts.d* directory.

### facts.d or local facts

You can add static custom facts by adding static files to facts.d, or add dynamic facts by adding executable scripts to facts.d. For example, you can add a list of all users on a host to your facts by creating and running a script in facts.d.

To use facts.d, create an /etc/ansible/facts.d directory on the remote host or hosts. If you prefer a different directory, create it and specify it using the fact_path play keyword. Add files to the directory to supply your custom facts. All file names must end with .fact. The files can be JSON, INI, or executable files returning JSON.

To add static facts, simply add a file with the .fact extension. For example, create /etc/ansible/facts.d/preferences.fact with this content:

```d
[general]
asdf=1
bar=2
```

The next time fact gathering runs, your facts will include a hash variable fact named general with asdf and bar as members. To validate this, run the following:

```bash
ansible <hostname> -m ansible.builtin.setup -a "filter=ansible_local"
```

or

```yml
{{ ansible_local['preferences']['general']['asdf'] }}
```
