# sheetstorm-deployment

Scripts and configuration for sheetstorm deployment.

## Cloning the repositories

All below steps/instructions require local copies of `sheetstorm` and `sheetstorm-config` repositories.

## Deployment

### Prerequisites

#### Ansible

You need `ansible` package for run configuration playbooks. Install it from your system package manager

### Creating `sheetstorm` machine

This step creates a machine for sheetstorm and mounts additional disk for postgresql backups.

```bash
 cd sheetstorm/sheetstorm-deployment/
 ansible-playbook create-compute-instance-for-sheetstorm.yml
```

### Configuring `sheetstorm` machine

This step configures machine for sheetstorm app.

```bash
 cd sheetstorm/sheetstorm-deployment/
ansible-playbook configure.yml                            \
    --inventory ../../sheetstorm-config/ansible_inventory \
    --user      $user
```

### Deploying to the `sheetstorm` machine

This step has a few options to execute, for default it's updates sheetstorm application to master version.
To control version of sheetstorm set the `$sheetstorm_version` shell variable.
Additional options:
- `$upload_secret_file` - this option requires knowledge of vault password and using additional `--ask-vault-pass` flag
- `$generate_static_files`
- `$migrate_database`

To execute additional options set shell variable to `yes` value.

```bash
cd sheetstorm/sheetstorm-deployment/
ansible-playbook deploy.yml                                        \
    --extra-vars sheetstorm_version=$sheetstorm_version            \
    --extra-vars upload_secret_file=$upload_secret_file            \
    --extra-vars generate_static_files=$generate_static_files      \
    --extra-vars migrate_database=$migrate_database                \
    --inventory  ../../sheetstorm-config/ansible_inventory         \
    --user       $user
```

## Sheetstorm Virtual Machine

The `sheetstorm-vm/` directory contains a Vagrant configuration that creates virtual machine with Sheetstorm set up.
The main task of the virtual machine is to test, debug on the reconstructed google compute instance environment.

### Prerequisites

#### Vagrant

You need to install `Vagrant` package from your system package manager.

#### VirtulBox

The virtual machine runs on VirtualBox. Install it from your system package manager.

VirtualBox provides several kernel modules and requires them, before you can start virtual machine.
These modules are connect with your specific linux kernel version and must be rebuild after your kernel version is changed.
To avoid that situation, you can do this automatically by using DKMS version. Most linux distributions provide a package named
`virtualbox-dmks` or `virtualbox-host-dkms` that provides module sources and configures your system to build them.

To be able to build the modules you also need kernel headers. The package contains them is called `linux-headers` on Arch Linux.
The other distributions contain additionally kernel version.

```bash
sudo apt-get install virtualbox-dkms linux-headers-x.y.z-w
```

The modules are not loaded automatically after the installation.
If you have a problem with running VirtualBox, try to load `vboxdrv` kernel module manually first.

```bash
sudo modprobe vboxdrv
```
The step above is not require after you restart system.

#### VirtualBox Guest Additions

This package provides a set of additional drivers and software that improve performance.
The package is called `virtualbox-guest-additions-iso` or `virtualbox-guest-iso` depends on distribution of linux.

```bash
sudo apt-get install virtualbox-guest-additions-iso
```

#### Create and configure the machine

This step creates and configures virtual machine with sheetstorm application.
You can also add additional options:

```bash
export SHEETSTORM_VERSION=<sheetstorm_version>
export RESET_DATABASE=true
```
To run configuration process use the following command:

```bash
vagrant up
```

#### Useful Commands

To stop the machine use the following command:

```bash
vagrant halt
```

To reconfiguring the machine use the following command:

```bash
vagrant provision
```

To restart the machine use the following command:

```bash
vagrant reload
```

To gets to the machine use the following command:

```bash
vagrant ssh
```

#### Helper script

```bash
run-sheetstorm.sh
```
This script starts Sheetstorm application in the virtual machine.
