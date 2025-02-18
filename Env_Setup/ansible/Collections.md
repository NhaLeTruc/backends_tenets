# Ansible Collections

An Ansible collection is a distribution format that bundles together Ansible content such as playbooks, roles, modules, and plugins into a single package. It provides a way to organize and share Ansible content in a modular and versioned manner. Collections are designed to make it easier to manage and share reusable automation content across different projects, teams, and organizations.

A typical collection addresses a set of related use cases. For example, the cisco.ios collection automates management of Cisco IOS devices. You can create a collection and publish it to Ansible Galaxy or to a private Automation Hub instance. You can publish certified collections to the Red Hat Automation Hub, part of the Red Hat Ansible Automation Platform.

In the context of Ansible, here are some key points about collections:

- **Modularity**: Collections allow you to organize Ansible content into logical units. This makes it easier to manage and share specific components of automation, like roles, modules, and plugins.
- **Versioning**: Collections can have different versions, enabling better control over the changes made to automation content. This is crucial for maintaining stability and consistency in your infrastructure automation processes.
- **Distribution**: Ansible collections can be shared through various channels, including the Ansible Galaxy community website. This encourages collaboration and the sharing of best practices among the Ansible user community.
- **Content Types**: Collections can contain various types of content, including modules (the building blocks of Ansible automation), plugins (to extend Ansible functionality), roles (pre-packaged automation tasks), and playbooks (orchestration of tasks).
- **Dependencies**: Collections can have dependencies on other collections or specific versions of Ansible. This ensures that the required automation components are available for successful execution.
- **Namespace**: Collections introduce a namespace structure to avoid naming conflicts between different authors and organizations. This helps in organizing content and avoiding clashes in names.

## Collection Structure

An Ansible Content Collection can be described as a package format for Ansible content:

- **docs/**: local documentation for the collection
- **galaxy.yml**: source data for the MANIFEST.json that will be part of the collection package
- **playbooks/**: playbooks reside here
- **tasks/**: this holds ‘task list files’ for include_tasks/import_tasks usage
- **plugins/**: all ansible plugins and modules go here, each in its own subdir
- **modules/**: ansible modules
- **lookups/**: lookup plugins
- **filters/**: Jinja2 filter plugins
- **connection/**: connection plugins required if not using default
- **roles/**: directory for ansible roles
- **tests/**: tests for the collection’s content

### Galaxy.yml

A Collection should have a galaxy.xml containing the necessary information to build a collection artefact. It is a file at the root level of the collection that holds the metadata and tools to package and publish the collection. It contains the following keys in YAML format.

Details on other directory and files in Ansible Collection structure can be found [here](https://www.devopsschool.com/blog/what-is-ansible-collection/)

## Create a Ansible Collection

1. Create a collection skeleton with the "ansible-galaxy collection init" command.
2. Add modules and other content to the collection.
3. Build the collection into a collection artifact with "ansible-galaxy collection build".
4. Publish the collection artifact to Galaxy with "ansible-galaxy collection publish".

## Creating a collection skeleton

```bash
ansible-galaxy collection init my_namespace.my_collection
```

Reference: the ansible-galaxy collection command. Currently the ansible-galaxy collection command implements the following sub commands:

- **init**: Create a basic collection skeleton based on the default template included with Ansible or your own template.
- **build**: Create a collection artifact that can be uploaded to Galaxy or your own repository.
- **publish**: Publish a built collection artifact to Galaxy.
- **install**: Install one or more collections.
