# Dietpi template

## Create empty VM

1. Create VM in Proxmox UI.
2. Do not use OS media.
3. System: Machine - q35; Qemu Agent - Yes.
4. CPU - 2 x 2
5. Memoery - 4096MB
6. Create VM.
7. Choose newly created VM. Detach disk.

## Config in VM console

[guide](https://dietpi.com/docs/install/#2-flash-the-dietpi-image)

1. apt update
2. apt full-upgrade
3. apt install xz-utils
4. curl Dietpi image.
5. Extract and import Dietpi image.

**NOTE: Follow guide for latest they are updated quite often**

## Import Dietpi image

```bash
qm importdisk "$VMID" DietPi_Proxmox-x86_64-Bookworm.qcow2 local-lvm --format=qcow2
```

