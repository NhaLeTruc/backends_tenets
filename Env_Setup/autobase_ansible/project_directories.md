# Ansible Project Directory

Folder PATH listing
Volume serial number is 0E43-0E9F
E:.
|   .dockerignore
|   add_balancer.yml
|   add_pgnode.yml
|   ansible.cfg
|   balancers.yml
|   changelog.yaml
|   config_pgcluster.yml
|   consul.yml
|   deploy_pgcluster.yml
|   Dockerfile
|   entrypoint.sh
|   etcd_cluster.yml
|   galaxy.yml
|   inventory.example
|   pg_upgrade.yml
|   pg_upgrade_rollback.yml
|   README.md
|   remove_cluster.yml
|   requirements.txt
|   requirements.yml
|   tags.md
|   tf_ansible_inventory
|   tree_output.md
|   update_pgcluster.yml
|   
+---files
|       requirements.txt
|       
+---meta
|       runtime.yml
|       
+---module_utils
|   |   urls.py
|   |   
|   \---common
|           file.py
|           
+---molecule
|   +---default
|   |       cleanup.yml
|   |       converge.yml
|   |       molecule.yml
|   |       prepare.yml
|   |       verify.yml
|   |       
|   +---pg_upgrade
|   |       converge.yml
|   |       molecule.yml
|   |       prepare.yml
|   |       
|   +---postgrespro
|   |   |   converge.yml
|   |   |   molecule.yml
|   |   |   prepare.yml
|   |   |   
|   |   \---vars
|   |           postgrespro_vars.yml
|   |           
|   \---tests
|       +---etcd
|       |       etcd.yml
|       |       
|       +---patroni
|       |       patroni.yml
|       |       
|       +---postgres
|       |       postgres.yml
|       |       replication.yml
|       |       
|       +---roles
|       |   +---confd
|       |   |   |   main.yml
|       |   |   |   
|       |   |   \---variables
|       |   |           haproxy.tmpl.yml
|       |   |           
|       |   +---deploy-finish
|       |   |   |   main.yml
|       |   |   |   
|       |   |   \---variables
|       |   |           haproxy_nodes.yml
|       |   |           
|       |   +---haproxy
|       |   |   |   main.yml
|       |   |   |   
|       |   |   \---variables
|       |   |           haproxy.cfg.yml
|       |   |           
|       |   +---patroni
|       |   |   |   main.yml
|       |   |   |   
|       |   |   \---variables
|       |   |           custom_wal_dir.yml
|       |   |           
|       |   +---pre-checks
|       |   |   |   main.yml
|       |   |   |   
|       |   |   \---variables
|       |   |           pgbouncer.yml
|       |   |           timescaledb.yml
|       |   |           
|       |   \---swap
|       |       |   main.yml
|       |       |   
|       |       \---conditions
|       |               create.yml
|       |               delete.yml
|       |               
|       \---variables
|           |   main.yml
|           |   
|           \---asserts
|                   apt_repository.yml
|                   baseurl.yml
|                   pg_probackup.yml
|                   system_info.yml
|                   vip_manager_package_repo.yml
|                   wal_g_cron_jobs.yml
|                   
+---plugins
|   \---callback
|           json_log.py
|           
\---roles
    +---add_repository
    |   |   README.md
    |   |   
    |   +---library
    |   |       deb822_repository.py
    |   |       
    |   \---tasks
    |           extensions.yml
    |           main.yml
    |           
    +---authorized_keys
    |   |   README.md
    |   |   
    |   +---defaults
    |   |       main.yml
    |   |       
    |   \---tasks
    |           main.yml
    |           
    +---cloud_resources
    |   |   README.md
    |   |   
    |   +---defaults
    |   |       main.yml
    |   |       
    |   \---tasks
    |           aws.yml
    |           azure.yml
    |           digitalocean.yml
    |           gcp.yml
    |           hetzner.yml
    |           inventory.yml
    |           main.yml
    |           
    +---common
    |   |   README.md
    |   |   
    |   \---defaults
    |           Debian.yml
    |           main.yml
    |           RedHat.yml
    |           system.yml
    |           upgrade.yml
    |           
    +---confd
    |   |   README.md
    |   |   
    |   +---defaults
    |   |       main.yml
    |   |       
    |   +---handlers
    |   |       main.yml
    |   |       
    |   +---tasks
    |   |       main.yml
    |   |       
    |   \---templates
    |           confd.service.j2
    |           confd.toml.j2
    |           haproxy.tmpl.j2
    |           haproxy.toml.j2
    |           
    +---consul
    |   |   CHANGELOG.md
    |   |   CONTRIBUTING.md
    |   |   CONTRIBUTORS.md
    |   |   LICENSE.txt
    |   |   README.md
    |   |   requirements.txt
    |   |   version.txt
    |   |   
    |   +---defaults
    |   |       main.yml
    |   |       
    |   +---files
    |   |       README.md
    |   |       
    |   +---handlers
    |   |       main.yml
    |   |       reload_consul_conf.yml
    |   |       restart_consul.yml
    |   |       restart_consul_mac.yml
    |   |       restart_rsyslog.yml
    |   |       restart_syslogng.yml
    |   |       start_consul.yml
    |   |       start_consul_mac.yml
    |   |       start_snapshot.yml
    |   |       stop_consul_mac.yml
    |   |       
    |   +---tasks
    |   |       acl.yml
    |   |       asserts.yml
    |   |       config.yml
    |   |       config_windows.yml
    |   |       dirs.yml
    |   |       dnsmasq.yml
    |   |       encrypt_gossip.yml
    |   |       install.yml
    |   |       install_linux_repo.yml
    |   |       install_remote.yml
    |   |       install_windows.yml
    |   |       iptables.yml
    |   |       main.yml
    |   |       nix.yml
    |   |       services.yml
    |   |       snapshot.yml
    |   |       syslog.yml
    |   |       tls.yml
    |   |       user_group.yml
    |   |       windows.yml
    |   |       
    |   +---templates
    |   |       config.json.j2
    |   |       configd_50acl_policy.hcl.j2
    |   |       configd_50custom.json.j2
    |   |       consul_bsdinit.j2
    |   |       consul_debianinit.j2
    |   |       consul_launchctl.plist.j2
    |   |       consul_smf_manifest.j2
    |   |       consul_snapshot.json.j2
    |   |       consul_systemd.service.j2
    |   |       consul_systemd_service.override.j2
    |   |       consul_systemd_snapshot.service.j2
    |   |       consul_sysvinit.j2
    |   |       dnsmasq-10-consul.j2
    |   |       rsyslogd_00-consul.conf.j2
    |   |       service.json.j2
    |   |       syslogng_consul.conf.j2
    |   |       
    |   \---vars
    |           Amazon.yml
    |           Archlinux.yml
    |           Darwin.yml
    |           Debian.yml
    |           Flatcar.yml
    |           FreeBSD.yml
    |           main.yml
    |           RedHat.yml
    |           Solaris.yml
    |           VMware Photon OS.yml
    |           Windows.yml
    |           
    +---copy
    |   |   README.md
    |   |   
    |   \---tasks
    |           main.yml
    |           
    +---cron
    |   |   README.md
    |   |   
    |   +---defaults
    |   |       main.yml
    |   |       
    |   \---tasks
    |           main.yml
    |           
    +---deploy_finish
    |   |   README.md
    |   |   
    |   \---tasks
    |           main.yml
    |           
    +---etcd
    |   |   README.md
    |   |   
    |   +---defaults
    |   |       main.yml
    |   |       
    |   +---tasks
    |   |       main.yml
    |   |       
    |   \---templates
    |           etcd.conf.j2
    |           etcd.service.j2
    |           
    +---etc_hosts
    |   |   README.md
    |   |   
    |   \---tasks
    |           main.yml
    |           
    +---firewall
    |   |   .gitignore
    |   |   .travis.yml
    |   |   .yamllint
    |   |   LICENSE
    |   |   README.md
    |   |   
    |   +---defaults
    |   |       main.yml
    |   |       
    |   +---handlers
    |   |       main.yml
    |   |       
    |   +---tasks
    |   |       disable-other-firewalls.yml
    |   |       main.yml
    |   |       
    |   \---templates
    |           firewall.bash.j2
    |           firewall.init.j2
    |           firewall.unit.j2
    |           
    +---haproxy
    |   |   README.md
    |   |   
    |   +---handlers
    |   |       main.yml
    |   |       
    |   +---tasks
    |   |       main.yml
    |   |       
    |   \---templates
    |           haproxy.cfg.j2
    |           haproxy.service.j2
    |           
    +---hostname
    |   |   README.md
    |   |   
    |   \---tasks
    |           main.yml
    |           
    +---io_scheduler
    |   |   README.md
    |   |   
    |   +---handlers
    |   |       main.yml
    |   |       
    |   +---tasks
    |   |       main.yml
    |   |       
    |   \---templates
    |           io-scheduler.service.j2
    |           
    +---keepalived
    |   |   README.md
    |   |   
    |   +---defaults
    |   |       main.yml
    |   |       
    |   +---handlers
    |   |       main.yml
    |   |       
    |   +---tasks
    |   |       main.yml
    |   |       
    |   \---templates
    |           keepalived.conf.j2
    |           
    +---locales
    |   |   README.md
    |   |   
    |   \---tasks
    |           main.yml
    |           
    +---mount
    |   |   README.md
    |   |   
    |   +---defaults
    |   |       main.yml
    |   |       
    |   \---tasks
    |           main.yml
    |           
    +---netdata
    |   |   README.md
    |   |   
    |   +---tasks
    |   |       main.yml
    |   |       
    |   \---templates
    |           netdata.conf.j2
    |           
    +---ntp
    |   |   README.md
    |   |   
    |   +---handlers
    |   |       main.yml
    |   |       
    |   +---tasks
    |   |       main.yml
    |   |       
    |   \---templates
    |           chrony.conf.j2
    |           ntp.conf.j2
    |           
    +---packages
    |   |   README.md
    |   |   
    |   +---defaults
    |   |       main.yml
    |   |       
    |   \---tasks
    |           extensions.yml
    |           main.yml
    |           perf.yml
    |           
    +---pam_limits
    |   |   README.md
    |   |   
    |   \---tasks
    |           main.yml
    |           
    +---patroni
    |   |   README.md
    |   |   
    |   +---config
    |   |   \---tasks
    |   |           main.yml
    |   |           pg_hba.yml
    |   |           
    |   +---handlers
    |   |       main.yml
    |   |       
    |   +---library
    |   |       yedit.py
    |   |       
    |   +---tasks
    |   |       custom_wal_dir.yml
    |   |       main.yml
    |   |       pip.yml
    |   |       
    |   \---templates
    |           patroni.service.j2
    |           patroni.yml.j2
    |           pg_hba.conf.j2
    |           
    +---pgbackrest
    |   |   README.md
    |   |   
    |   +---stanza-create
    |   |   \---tasks
    |   |           main.yml
    |   |           
    |   +---tasks
    |   |       auto_conf.yml
    |   |       bootstrap_script.yml
    |   |       cron.yml
    |   |       main.yml
    |   |       ssh_keys.yml
    |   |       
    |   \---templates
    |           pgbackrest.conf.j2
    |           pgbackrest.server.conf.j2
    |           pgbackrest.server.stanza.conf.j2
    |           pgbackrest_bootstrap.sh.j2
    |           
    +---pgbouncer
    |   |   README.md
    |   |   
    |   +---config
    |   |   |   README.md
    |   |   |   
    |   |   \---tasks
    |   |           main.yml
    |   |           
    |   +---handlers
    |   |       main.yml
    |   |       
    |   +---tasks
    |   |       main.yml
    |   |       
    |   \---templates
    |           pgbouncer.ini.j2
    |           pgbouncer.service.j2
    |           userlist.txt.j2
    |           
    +---pgpass
    |   |   README.md
    |   |   
    |   \---tasks
    |           main.yml
    |           
    +---pg_probackup
    |   |   README.md
    |   |   
    |   \---tasks
    |           main.yml
    |           
    +---postgresql_databases
    |   |   README.md
    |   |   
    |   \---tasks
    |           main.yml
    |           
    +---postgresql_extensions
    |   |   README.md
    |   |   
    |   \---tasks
    |           main.yml
    |           
    +---postgresql_privs
    |   |   README.md
    |   |   
    |   \---tasks
    |           main.yml
    |           
    +---postgresql_schemas
    |   |   README.md
    |   |   
    |   \---tasks
    |           main.yml
    |           
    +---postgresql_users
    |   |   README.md
    |   |   
    |   \---tasks
    |           main.yml
    |           
    +---pre_checks
    |   |   README.md
    |   |   
    |   \---tasks
    |           extensions.yml
    |           huge_pages.yml
    |           main.yml
    |           passwords.yml
    |           patroni.yml
    |           pgbackrest.yml
    |           pgbouncer.yml
    |           wal_g.yml
    |           
    +---resolv_conf
    |   |   README.md
    |   |   
    |   \---tasks
    |           main.yml
    |           
    +---ssh_keys
    |   |   README.md
    |   |   
    |   \---tasks
    |           main.yml
    |           
    +---sudo
    |   |   README.md
    |   |   
    |   \---tasks
    |           main.yml
    |           
    +---swap
    |   |   README.md
    |   |   
    |   \---tasks
    |           main.yml
    |           
    +---sysctl
    |   |   README.md
    |   |   
    |   \---tasks
    |           main.yml
    |           
    +---timezone
    |   |   README.md
    |   |   
    |   \---tasks
    |           main.yml
    |           
    +---tls_certificate
    |   |   README.md
    |   |   
    |   +---copy
    |   |   |   README.md
    |   |   |   
    |   |   \---tasks
    |   |           main.yml
    |   |           
    |   \---generate
    |       |   README.md
    |       |   
    |       \---tasks
    |               main.yml
    |               
    +---transparent_huge_pages
    |   |   README.md
    |   |   
    |   +---handlers
    |   |       main.yml
    |   |       
    |   \---tasks
    |           main.yml
    |           
    +---update
    |   |   README.md
    |   |   
    |   +---tasks
    |   |       extensions.yml
    |   |       patroni.yml
    |   |       pgbackrest_host.yml
    |   |       postgres.yml
    |   |       pre_checks.yml
    |   |       start_services.yml
    |   |       start_traffic.yml
    |   |       stop_services.yml
    |   |       stop_traffic.yml
    |   |       switchover.yml
    |   |       system.yml
    |   |       update_extensions.yml
    |   |       
    |   \---vars
    |           main.yml
    |           
    +---upgrade
    |   |   README.md
    |   |   
    |   +---tasks
    |   |       checkpoint_location.yml
    |   |       custom_wal_dir.yml
    |   |       dcs_remove_cluster.yml
    |   |       extensions.yml
    |   |       initdb.yml
    |   |       maintenance_disable.yml
    |   |       maintenance_enable.yml
    |   |       packages.yml
    |   |       pgbouncer_pause.yml
    |   |       pgbouncer_resume.yml
    |   |       post_checks.yml
    |   |       post_upgrade.yml
    |   |       pre_checks.yml
    |   |       rollback.yml
    |   |       schema_compatibility.yml
    |   |       ssh-keys.yml
    |   |       start_services.yml
    |   |       statistics.yml
    |   |       stop_services.yml
    |   |       update_config.yml
    |   |       update_extensions.yml
    |   |       upgrade_check.yml
    |   |       upgrade_primary.yml
    |   |       upgrade_secondary.yml
    |   |       
    |   \---templates
    |           haproxy-no-http-checks.cfg.j2
    |           
    +---vip_manager
    |   |   README.md
    |   |   
    |   +---defaults
    |   |       main.yml
    |   |       
    |   +---disable
    |   |   \---tasks
    |   |           main.yml
    |   |           
    |   +---handlers
    |   |       main.yml
    |   |       
    |   +---tasks
    |   |       main.yml
    |   |       
    |   \---templates
    |           vip-manager.service.j2
    |           vip-manager.yml.j2
    |           
    \---wal_g
        |   README.md
        |   
        +---defaults
        |       main.yml
        |       
        +---tasks
        |       auto_conf.yml
        |       cron.yml
        |       main.yml
        |       
        \---templates
                walg.json.j2
                
