# Terraform Setup

```bash

apt update && apt install -y lsb-release && apt clean all

wget -O - https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list
apt install terraform

# In case of fuckups undo by
rm /usr/share/keyrings/hashicorp-archive-keyring.gpg
rm /etc/apt/sources.list.d/hashicorp.list

```

## Notes

1. 