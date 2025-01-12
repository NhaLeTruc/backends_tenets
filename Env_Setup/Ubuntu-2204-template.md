# Create a Ubuntu 2204 VM template

## References

[Youtube Guide](https://www.youtube.com/watch?v=MJgIm03Jxdo)
[CMD Guide](https://technotim.live/posts/cloud-init-cloud-image/)
[Ubuntu Cloud Images](https://cloud-images.ubuntu.com/releases/)

## Steps

1. Setup an empty VM (no disk no OS) in Proxmox UI or CLI. See vid for step by step.
2. Download VM image e.g. [image](https://cloud-images.ubuntu.com/minimal/releases/jammy/release/) in Proxomox CLI.
3. Guide dont know why but it is needed: Change the file extension of the image to .qcow2
4. Resize the downloaded cloud image storage size to 8-32GB (enough for most usecases).
5. Import the cloud image into empty VM. Note that storage option must support file system (**Not lvm-thin**), so that .qcow2 images could work.
6. Go to **VM ID >> Hardware >>** find **Unused disk**. Double click to edit, and click add. Note that if storage is of SSD type tick **discard** and **SSD emulation** before adding.
7. Stay in **Hardware** and add one **CloudInit Drive**. Choose lvm-thin storage type.
8. Config VM login **username** and **password** in CloudInit tab.
9. Go to **Options** tab. Edit **Boot Order** to include new VM's Hard Disk. Move new disk to top in boot order.
10. Convert VM to template. DO NOT START.
11. Start full cloning.
12. Login into new VM instance and:
    1.  sudo apt install qemu-guest-agent
    2.  sudo nano /etc/ssh/sshd_config.d/60-cloudimg-settings.conf - Note that this conf filename is different from img to img.
        1.  PasswordAuthentication yes
        2.  PubkeyAuthentication yes
    3.  reboot

## Commands

```bash

wget https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img

# Change the file extension of the image to .qcow2
mv jammy-server-cloudimg-amd64.img jammy-server-cloudimg-amd64.qcow2

# Resize the downloaded cloud image
qemu-img resize jammy-server-cloudimg-amd64.qcow2 32G

# Import the cloud image into Proxmox
qm importdisk $VMID jammy-server-cloudimg-amd64.qcow2 local --format=qcow2

sudo apt install qemu-guest-agent

sudo nano /etc/ssh/sshd_config.d/60-cloudimg-settings.conf

#PasswordAuthentication yes
#PubkeyAuthentication yes

reboot

```

## More Readings

1. [proxmox-import-and-use-cloud-images](https://codingpackets.com/blog/proxmox-import-and-use-cloud-images/)
2. [differences between q35 and default](https://forum.proxmox.com/threads/q35-vs-i440fx.112147/)
3. [enable pubkey ssh](https://superuser.com/questions/1376201/how-do-i-force-ssh-to-use-password-instead-of-key)
