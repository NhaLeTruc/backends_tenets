# Ansible Templates

What are Ansible templates? Templates are useful in cases where we would like to reuse a file but with different parameters for various use cases or environments.

[Detailed Guide](https://spacelift.io/blog/ansible-template)

## Intro to Ansible Templating

With Ansible templating, users can dynamically generate text-based files using templates, variables, and facts for configuration and other purposes. The main objective of using templates is to facilitate and automate the management of configuration files for different targets and requirements.

Imagine that you need to maintain multiple similar environments but with different requirements or specifications. Instead of manually creating, maintaining, and editing configuration files for each target system, we can leverage Ansible templates. We can then combine the templates with other Ansible concepts, such as facts and variables, to generate files tailored to each system’s specific needs without code duplication.

Updating configuration files becomes more manageable with this approach since we only have to perform the changes in one place and handle any inputs with variables that will be replaced with actual values during the playbook execution.

Ansible uses Jinja2 as the default templating engine to create dynamic content.

## Templating with Jinja2

Jinja2 templates combine plain text files and special syntax to define and substitute dynamic content, embed variables, expressions, loops, and even conditional statements to generate complex output. According to the documentation, expressions are enclosed in double curly braces {{ }}, statements in curly braces with percent signs {% %}, and comments in {# #}.

Let’s have a look at some examples below:

```jinja
My favourite color is {{ favourite_color }}

{% if age > 18 %} 
You are an adult, and you can vote in the voting center: {{ voting_center }}
 {% else %}
Sorry, you are minor, and you can’t vote yet.
{% endif %}

Here’s a list of fruits:
{% for fruit in fruits %}
{{ fruit }}
{% endfor %} 
```

## Demo: Create and Use a Template in an Ansible Playbook

let’s see an example with a real use case. In the second example, we will use a template to create a configuration file for an Nginx web server.

- nginx.conf.j2

```jinja
server {
       listen {{ web_server_port }};
       listen [::]:{{ web_server_port }};
       root {{ nginx_custom_directory }};
       index index.html;
       location / {
               try_files $uri $uri/ =404;
       }
}
```

main_playbook.yml

```yml
- name: Provision nginx web server
  hosts: all
  gather_facts: yes
  become: yes
  vars:
    nginx_version: 1.18.0-0ubuntu1.4
    nginx_custom_directory: /home/ubuntu/nginx
    web_server_port: 80
  tasks:
  - name: Update and upgrade apt
    ansible.builtin.apt:
      update_cache: yes
      cache_valid_time: 3600
      upgrade: yes


  - name: "Install Nginx to version {{ nginx_version }}"
    ansible.builtin.apt:
      name: "nginx={{ nginx_version }}"
      state: present


  - name: Copy the Nginx configuration file to the host
    template:
      src: templates/nginx.conf.j2
      dest: /etc/nginx/sites-available/default
  
  - name: Create link to the new config to enable it
    file:
      dest: /etc/nginx/sites-enabled/default
      src: /etc/nginx/sites-available/default
      state: link


  - name: Create Nginx directory
    ansible.builtin.file:
      path: "{{ nginx_custom_directory }}"
      state: directory


  - name: Copy index.html to the Nginx directory
    copy:
      src: files/index.html
      dest: "{{ nginx_custom_directory }}/index.html"
  - name: Restart the Nginx service
    service:
      name: nginx
      state: restarted
```

index.html

```html
<html>
  <head>
    <title> Hello from Nginx </title>
  </head>
  <body>
  <h1> This is our test webserver</h1>
  <p>This nginx web server was deployed by Ansible.</p>
  </body>
</html>
```

Let’s go ahead and run this playbook.

```bash
ansible_template ansible-playbook main_playbook.yml
```

Last step, let’s ssh into the local host, verify that everything has run successfully, and check the file */etc/nginx/sites-available/default* generated from the template.

```bash
curl localhost

cat /etc/nginx/sites-available/default
```
