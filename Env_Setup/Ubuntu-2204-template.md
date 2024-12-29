# Create a Ubuntu 2204 VM template

[Youtube Guide](https://www.youtube.com/watch?v=MJgIm03Jxdo)

## Steps

1. Setup VM in Proxmox UI. See vid for step by step.
2. Setup ssh keys on Proxmox server [Github guide](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)
3. Download ubuntu VM [image](https://cloud-images.ubuntu.com/minimal/releases/jammy/release/) in Proxomox terminal or ssh.
4. Add a serial console to the reference VM.
5. Guide dont know why but it is needed: Change the file extension of the image to .qcow2
6. Resize the downloaded cloud image storage size.
7. Import the cloud image into Proxmox. Note that storage option (local-lvm) could be modified depend on usecases e.g. EFS/TrueNas/etc.
8. Go to **VM ID >> Hardware >>** find **Unused disk**. Double click to edit, and click add. Note that if storage is of SSD type tick **discard** and **SSD emulation** before adding.
9. Optional: Change **Start on boot** on so all VM from this template with start at server boot.
10. Convert VM to template.

## Commands

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"

wget https://cloud-images.ubuntu.com/minimal/releases/jammy/release/ubuntu-22.04-minimal-cloudimg-amd64.img

# Add a serial console to the reference VM
qm set <VM ID> --serial0 socket --vga serial0

# Change the file extension of the image to .qcow2
mv ubuntu-22.04-minimal-cloudimg-amd64.img ubuntu-22.04.qcow2

# Resize the downloaded cloud image
qemu-img resize ubuntu-22.04.qcow2 32G

# Import the cloud image into Proxmox
qm importdisk <VM ID> ubuntu-22.04.qcow2 local-lvm

```

## More Readings

1. [proxmox-import-and-use-cloud-images](https://codingpackets.com/blog/proxmox-import-and-use-cloud-images/)
