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

lvcreate -L 1000GB -ndata pve

lvconvert --type thin-pool --poolmetadatasize 15G /dev/pve/data

lvresize -l +100%FREE /dev/pve/data

```

- Create new thin-pool lvm in **Datacenter > Storage**
- Note that 1000GB for pve/data is base on ~1.7TB disk. The idea is to give room for pve to perform the conversion to thin-pool type lvm.
- Note the free space is later claimed by pve/data.
- Note max poolmetadatasize is 15.88GB as of proxmox 8.3
- A few cmd to check disks/volumes configuration:

```bash
pvs
vgs
lvs
lsblk
fdisk -l
```

## Install Dietpi

[MRP's guide](https://www.youtube.com/watch?v=yIRezNGXFGE)
[Official guide](https://dietpi.com/docs/install/#how-to-install-dietpi-proxmox)

1. Select the Proxmox node, then click the Shell button at the top right corner. Alternatively connect via SSH to the Proxmox server, using the same login credentials you used for the Proxmox web interface.
2. In the console window, enter the following commands to download the DietPi image, optionally check its integrity, decompress it via xz, import it as disk to your new VM (using the VM ID you chose during creation) and make it the boot drive.

```bash
apt update
apt full-upgrade
apt install xz-utils
curl -O https://dietpi.com/downloads/images/DietPi_Proxmox-x86_64-Bookworm.qcow2.xz
sha256sum -c <(curl -sSf 'https://dietpi.com/downloads/images/DietPi_Proxmox-x86_64-Bookworm.qcow2.xz.sha256')
xz -d DietPi_Proxmox-x86_64-Bookworm.qcow2.xz
```

Next, the disk image is imported.
Note: Replace 100 below with the VM ID entered during VM creation.

```bash
ID=100
qm importdisk "$ID" DietPi_Proxmox-x86_64-Bookworm.qcow2 local-lvm
qm set "$ID" --scsi0 "local-lvm:vm-$ID-disk-0"
qm set "$ID" --boot order=scsi0
```

The VM can now be started, select it via left side navigation of the Proxmox web interface, then the Start button at the top right side, finally the Console button to watch and finish the DietPi first run setup.
Alternatively you can connect to the VM via SSH, after giving it some time to finish initial setup steps and obtaining its IP with your router or IP scanner.
