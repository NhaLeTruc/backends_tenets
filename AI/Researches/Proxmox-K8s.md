# Proxmox Kubernetes (proxmox-k8s)

an Infrastructure as Code project that automates deploying production-ready Kubernetes clusters on Proxmox VE hypervisor.

🎯 Purpose
Provides a declarative, repeatable way to create complete K8s clusters on Proxmox infrastructure using Terraform (infrastructure provisioning) + Kubespray (Kubernetes installation).

🏗️ Architecture
Tech Stack:

Terraform (>= 1.3.3) with Proxmox provider
Kubespray v2.25.0 (runs in Docker container)
Kubernetes v1.29.5 (default)
Ubuntu 24.04 VMs with cloud-init
Containerd runtime with ipvs proxy mode
Default Cluster:

1 control plane node (2 vCPU, 1.5GB RAM)
2 worker nodes (2 vCPU, 2GB RAM each)
1 dedicated Kubespray host for installation
Network: 10.0.1.0/24 (configurable)
📁 Structure
proxmox-k8s/
├── modules/proxmox_ubuntu_vm/  # Reusable VM module
├── kubespray/                   # Config templates (inventory, k8s-cluster, addons)
├── scripts/                     # Setup and install scripts
├── .github/workflows/           # CI/CD pipelines
├── vm-k8s-nodes.tf             # Control plane & worker definitions
├── vm-kubespray-host.tf        # Installation host
└── Makefile                     # Build automation
✨ Key Features
Multi-host deployment - Distribute VMs across multiple Proxmox nodes (round-robin)
Bastion host support - SSH through jump host for private networks
Flexible networking - Configurable MTU, multiple CNI options (Calico, Cilium, Flannel, Weave)
Optional add-ons - Helm, Nginx Ingress, ArgoCD, MetalLB, Cert Manager
Backward compatibility - Legacy naming convention support for v3.x clusters
CPU/Memory hotplug - Dynamic resource scaling
🔍 Notable Design Patterns
Template-driven configuration - Terraform generates Kubespray configs dynamically
Separation of concerns - Reusable module, separate node type files
Idempotent infrastructure - Declarative Terraform + Ansible playbooks
Always-run trigger - Forces cluster config drift correction on every apply
📊 Code Quality
Strengths:

Well-documented (comprehensive README with auto-generated variable docs)
Active CI/CD (terraform fmt/validate/lint, automated releases)
Pre-commit hooks for code quality
Clean, modular architecture
Production-ready with sensible defaults
Gaps:

No automated testing (only linting)
No remote state backend configuration
Limited secrets management (credentials in tfvars)
No built-in monitoring/logging stack
Manual kubeconfig retrieval
🚀 Recent Activity
Multi-host deployment support (PR #107)
MTU configuration options (PR #106)
Proxmox 8.2.4 compatibility
Code quality improvements
💡 Assessment
Overall Quality: High-quality, production-ready IaC project

Best suited for:

On-premises K8s for enterprises using Proxmox
Dev/staging clusters
Cost-effective alternative to cloud K8s
Project Maturity: Version 5.0.0+, well-maintained, active community contributions

This is a solid, well-architected project that effectively bridges Proxmox virtualization with Kubernetes orchestration using modern IaC practices. The code is clean, maintainable, and follows Terraform best practices.

## alternative open-source tech stacks for deploying Kubernetes on Proxmox

Current Stack Assessment
What this project uses:

Terraform + Proxmox Provider (infrastructure)
Kubespray (Kubernetes installation)
Ubuntu VMs with cloud-init
Containerd runtime
Pros: Mature, well-documented, flexible, separation of concerns Cons: Two-layer complexity (Terraform + Ansible), requires dedicated Kubespray VM, manual kubeconfig retrieval

Alternative Tech Stacks
1. Talos Linux + Terraform ⭐ (Best Modern Alternative)
Stack:

Terraform + Proxmox Provider (infrastructure)
Talos Linux (immutable OS designed specifically for K8s)
How it works:

Talos is a minimal Linux distro with no SSH, no shell, no package manager
Entire OS configured via API
K8s is built-in, not installed on top of Ubuntu
Managed via talosctl CLI
Advantages:

Simpler: No Kubespray VM needed, no Ansible layer
More secure: No SSH access, smaller attack surface, immutable OS
Faster: Boots in seconds, K8s already integrated
Less overhead: ~500MB RAM for OS vs Ubuntu's overhead
API-driven: Everything configured declaratively via Talos config
Better upgrades: Atomic OS updates, A/B partition scheme
Native HA: Built-in etcd and control plane HA
Disadvantages:

Newer ecosystem: Less mature than Ubuntu + Kubespray (but growing fast)
Learning curve: Different mental model (no SSH means new debugging approach)
Less flexible: Can't customize base OS like traditional Linux
Verdict: This is arguably the best modern approach for production K8s on Proxmox. More cloud-native, simpler architecture, better security posture.

2. Cluster API (CAPI) + Proxmox Provider
Stack:

Kubernetes Cluster API (K8s-native cluster management)
CAPI Provider for Proxmox
Management cluster bootstrapped with kind/k3s
How it works:

Deploy a small "management" K8s cluster first
Use K8s CRDs to define infrastructure (like Terraform resources)
CAPI controllers create VMs and install K8s automatically
Everything is Kubernetes YAML manifests
Advantages:

K8s-native: Manage clusters the same way you manage applications
GitOps ready: Perfect for ArgoCD/Flux workflows
Consistent API: Same approach works for AWS, Azure, VMware, etc.
Self-healing: Controllers continuously reconcile desired state
Scaling: Built-in MachineDeployment for node autoscaling
Disadvantages:

Complexity: Requires bootstrap cluster (chicken-and-egg problem)
Proxmox CAPI provider less mature: Not as polished as AWS/Azure providers
Overhead: Running a management cluster just to manage other clusters
Steeper learning curve: Need to understand CAPI concepts (Machines, MachineSets, etc.)
Verdict: Excellent for multi-cluster environments or if you're already deep in the K8s ecosystem. Overkill for single cluster deployments.

3. OpenTofu + Kubespray (Terraform Alternative)
Stack:

OpenTofu (open-source Terraform fork, post-license change)
Same Kubespray approach
How it works:

Drop-in replacement for Terraform
Exact same HCL syntax
Community-driven, Linux Foundation project
Advantages:

Truly open source: MPL 2.0 license vs Terraform's BSL
Community governance: Not controlled by single vendor
Compatible: Can use existing .tf files
Future-proof: No risk of HashiCorp license changes
Disadvantages:

Fragmentation: Terraform still dominates, ecosystem split
Maturity: Newer project (forked in 2023)
Provider lag: Some providers slower to update for OpenTofu
Verdict: Ethical/philosophical choice more than technical. Good if avoiding vendor lock-in concerns with HashiCorp.

4. Pulumi + Kubernetes Operator
Stack:

Pulumi (IaC using real programming languages: Python, Go, TypeScript)
Pulumi Kubernetes provider
Direct kubeadm or k3s installation
How it works:

Write infrastructure code in Python/Go/TypeScript instead of HCL
Use loops, functions, classes, type checking
Install K8s via Pulumi's remote command provider or Kubernetes operator
Advantages:

Real programming: Loops, conditionals, functions, testing, IDE support
Type safety: Catch errors before deployment
Reusability: NPM/PyPI packages instead of Terraform modules
Unified language: Same language for infra and apps
Better testing: Unit tests with standard frameworks
Disadvantages:

Learning curve: Need to know Python/Go/TypeScript AND infrastructure
Smaller community: Terraform has more examples and modules
State management: Different paradigm than Terraform
Team skills: Requires programming background
Verdict: Excellent if your team is developer-heavy rather than ops-heavy. Better for complex, dynamic infrastructure.

5. Terraform + k3s (Lightweight Alternative)
Stack:

Terraform + Proxmox Provider
k3s (lightweight K8s from Rancher/SUSE)
Simple shell script installation (no Ansible)
How it works:

Create VMs with Terraform
k3s installs via single curl command
Automatic HA with embedded etcd
Built-in Traefik, CoreDNS, local storage
Advantages:

Simpler: No Kubespray, no Ansible, just shell script
Lighter: ~512MB RAM per node vs 1.5GB for full K8s
Faster: Installs in seconds
Batteries included: Load balancer, ingress, storage out of box
Edge-friendly: Designed for ARM, IoT, edge computing
Disadvantages:

Different from upstream K8s: Some compatibility differences
Less customizable: Opinionated defaults
Smaller ecosystem: Fewer resources than full K8s
Not suitable for all workloads: Some enterprise features missing
Verdict: Perfect for dev/test environments or resource-constrained setups. Production-ready but different philosophy.

6. Terraform + RKE2
Stack:

Terraform + Proxmox Provider
RKE2 (Rancher Kubernetes Engine 2, SUSE's enterprise K8s)
Shell script or Ansible for installation
How it works:

Similar to current approach but RKE2 instead of Kubespray
RKE2 is hardened K8s (meets CIS, FIPS, STIG standards)
Single binary installation
Built-in security policies
Advantages:

Security hardened: Meets government/compliance standards
Simpler than Kubespray: Single binary, less Ansible complexity
Production support: Commercial support from SUSE available
Fully compatible: 100% upstream K8s
Embedded etcd: HA without external etcd
Disadvantages:

Rancher-centric: Ecosystem tied to Rancher products
Less flexible: More opinionated than vanilla K8s
Smaller community: Less content than kubeadm/Kubespray
Verdict: Ideal for highly regulated industries (government, finance, healthcare) requiring security certifications.

7. Harvester HCI (Radical Alternative)
Stack:

Harvester (Hyper-Converged Infrastructure built on K8s)
Replaces Proxmox entirely
How it works:

Deploy Harvester instead of Proxmox
It's K8s + KubeVirt (VMs on K8s) + Longhorn storage
Manage VMs and containers from same platform
Web UI similar to Proxmox
Advantages:

Unified platform: One system for VMs and containers
K8s-native: VMs are K8s resources (Kubevirt)
Built-in storage: Longhorn distributed storage included
Modern architecture: Cloud-native from ground up
Rancher integration: Seamless multi-cluster management
Disadvantages:

Replace entire hypervisor: Can't run alongside Proxmox
Different paradigm: Not traditional virtualization
Migration effort: Need to move existing VMs
Maturity: Newer than Proxmox (first stable 2022)
Resource overhead: K8s layer adds overhead
Verdict: Revolutionary approach if starting fresh. Not suitable if you have existing Proxmox infrastructure you want to keep.

8. Ansible + kubadm (Simpler Than Kubespray)
Stack:

Terraform for VM provisioning
Simple Ansible playbook (not Kubespray)
Direct kubeadm commands
How it works:

Create VMs with Terraform
Write custom Ansible playbook (50-100 lines)
Run kubeadm init/join commands
Install CNI (Calico/Cilium) manually
Advantages:

Full control: Know exactly what's happening
Simpler: No Kubespray abstractions
Faster: Less overhead, direct commands
Educational: Learn K8s internals
Disadvantages:

Maintenance burden: You own the upgrade path
Less battle-tested: Kubespray has years of production use
Missing features: No advanced Kubespray features (CRI-O, custom DNS, etc.)
Reinventing wheel: Solving already-solved problems
Verdict: Good for learning or if you have specific requirements Kubespray doesn't support. Otherwise, use proven tools.

Comparative Matrix
| Stack | Complexity | Security | Maintenance | Production Ready | Learning Curve | |-------|-----------|----------|-------------|------------------|----------------| | Current (TF + Kubespray) | Medium | Good | Medium | ⭐⭐⭐⭐⭐ | Medium | | Talos + TF | Low | Excellent | Low | ⭐⭐⭐⭐⭐ | Medium | | CAPI + Proxmox | High | Good | Medium | ⭐⭐⭐ | High | | OpenTofu + Kubespray | Medium | Good | Medium | ⭐⭐⭐⭐ | Low (if know TF) | | Pulumi + K8s | Medium | Good | Medium | ⭐⭐⭐⭐ | High | | TF + k3s | Low | Good | Low | ⭐⭐⭐⭐ | Low | | TF + RKE2 | Low-Medium | Excellent | Low | ⭐⭐⭐⭐⭐ | Medium | | Harvester | High | Good | Medium | ⭐⭐⭐⭐ | High | | Ansible + kubeadm | Low | Good | High | ⭐⭐⭐ | Low |

Recommendations by Use Case
For Production, Security-Focused Environments:
➡️ Talos Linux + Terraform or RKE2 + Terraform

Best security posture, simpler architecture, lower maintenance
For Multi-Cluster/GitOps Shops:
➡️ Cluster API

K8s-native, scales to many clusters, GitOps-ready
For Dev/Test/Resource-Constrained:
➡️ k3s + Terraform

Fast, lightweight, simple, cost-effective
For Developer-Heavy Teams:
➡️ Pulumi

Real programming languages, better testing, type safety
For Regulatory Compliance (CIS/FIPS/STIG):
➡️ RKE2 + Terraform

Pre-hardened, meets compliance standards
To Avoid Vendor Lock-in:
➡️ OpenTofu + Kubespray

Drop-in Terraform replacement, community-governed
For Learning/Custom Requirements:
➡️ Ansible + kubeadm

Full understanding of internals, maximum control
My Opinion: Top 3 "Better" Alternatives
🥇 1. Talos Linux + Terraform
Why: Simpler architecture (no Kubespray layer), better security (immutable, no SSH), faster deployments, lower operational overhead. This is where the industry is heading for bare-metal/VM K8s.

Migration path from current: Replace Ubuntu template with Talos image, replace Kubespray with Talos config, remove Kubespray VM entirely.

🥈 2. Terraform + RKE2
Why: Simpler than Kubespray (single binary install), security-hardened out of box, fully compatible with upstream K8s, production support available. Good middle ground between current approach and Talos.

🥉 3. OpenTofu + Kubespray
Why: Keep what works, just swap Terraform for truly open-source alternative. Lowest risk change, future-proofs against HashiCorp licensing changes.

Should You Change?
If the current stack works for you: NO

Kubespray is battle-tested, well-documented, production-proven
Terraform + Kubespray is an industry-standard approach
Don't fix what isn't broken
Consider changing if:

You want better security posture → Talos or RKE2
You have many clusters to manage → CAPI
You need compliance certifications → RKE2
You're resource-constrained → k3s
You want simpler operations → Talos
You're concerned about HashiCorp licensing → OpenTofu
Bottom line: The current project is well-designed. Talos Linux would be the most significant upgrade in terms of simplicity, security, and operational efficiency, but requires rethinking the VM layer entirely.