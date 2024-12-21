# Setup New proxmox

## Basic Setups

Setup configs for free or subscribed repositories:
[Package_Repositories](https://pve.proxmox.com/wiki/Package_Repositories)

Setup configs for secure boot:
[Secure_Boot_Setup](https://pve.proxmox.com/wiki/Secure_Boot_Setup) 

## Resize local and lvm-thin storages

### Rationale

By default, proxmox allocates too much disk to lvm-thin which is used to create storages for VMs. While local directory storing everything else is typically sized to only 100GB. I want to adjust that to 300GB for future works.

- Delete lvm-thin storage: in **Datacenter > Storage** >> select and remove the default lvm-thin storage.
- Sorting storage script for resizing local and lvm-thin:

```bash
lvremove /dev/pve/data -y && lvresize -L +200GB /dev/pve/root && resize2fs /dev/mapper/pve-root

lvecreate -l +100%FREE -ndata pve

lvconvert --type thin-pool --poolmetadatasize 10G /dev/pve/data

```

- A few cmd to check disks/volumes configuration:

```bash
pvs
vgs
lvs
lsblk
fdisk -l
```
