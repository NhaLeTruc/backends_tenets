# Ansible Managed Services and APIs

There are many options for managing Ansible applications with a graphical UI. This is the main avenue for Cloud Service Providers and Consultancies to charge people for using Ansible professionally.

## RHAAP

Red Hat® Ansible® Automation Platform is a unified solution for strategic automation. It combines the security, features, integrations, and flexibility needed to scale automation across domains, orchestrate essential workflows, and optimize IT operations to successfully adopt enterprise AI.

[link](https://www.redhat.com/en/technologies/management/ansible?sc_cid=7015Y000003t7aWQAQ)

## Ansible AWX

Ansible AWX helps teams manage complex multi-tier deployments by adding control, knowledge, and delegation to Ansible-powered environments.

## AWX API

[link](https://ansible.readthedocs.io/projects/awx/en/latest/rest_api/index.html)

REST stands for Representational State Transfer and is sometimes spelled as “ReST”. It relies on a stateless, client-server, and cacheable communications protocol, usually the HTTP protocol.

You may find it helpful to see which API calls the user interface makes in sequence. To do this, you can use the UI from Firebug or Chrome with developer plugins.

## Ansible Runner

[link](https://ansible.readthedocs.io/projects/runner/en/latest/)

Ansible Runner is a tool and python library that helps when interfacing with Ansible directly or as part of another system whether that be through a container image interface, as a standalone tool, or as a Python module that can be imported. The goal is to provide a stable and consistent interface abstraction to Ansible. This allows Ansible to be embedded into other systems that don’t want to manage the complexities of the interface on their own (such as CI/CD platforms, Jenkins, or other automated tooling).

Ansible Runner represents the modularization of the part of **Ansible AWX** that is responsible for running ansible and ansible-playbook tasks and gathers the output from it. It does this by presenting a common interface that doesn’t change, even as Ansible itself grows and evolves.
