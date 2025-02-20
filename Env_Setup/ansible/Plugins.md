# Ansible Plugins

Similar to modules are plugins, which are pieces of code that extend core Ansible functionality. Ansible uses a plugin architecture to enable a rich, flexible, and expandable feature set. Ansible ships with several plugins and lets you easily use your own plugins.

the various types of plugins that are included with Ansible:

Action plugins
Become plugins
Cache plugins
Callback plugins
Cliconf plugins
Connection plugins
Docs fragments
Filter plugins
Httpapi plugins
Inventory plugins
Lookup plugins
Modules
Module utilities
Netconf plugins
Shell plugins
Strategy plugins
Terminal plugins
Test plugins
Vars plugins

## Developing plugins

All plugins must:

- be written in Python
- raise errors
- return strings in unicode
- conform to Ansible’s configuration and documentation standards

Once you’ve reviewed these general guidelines, you can skip to the particular type of plugin you want to develop.

Full Details for different type of plugin development [here](https://docs.ansible.com/ansible/latest/dev_guide/developing_plugins.html)
