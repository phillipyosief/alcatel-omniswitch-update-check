# Alcatel OmniSwitch Update Check Ansible Role
> Automated version checking and update validation for Alcatel-Lucent OmniSwitch devices (AOS6/AOS8)

[![Ansible Galaxy](https://img.shields.io/ansible/role/d/phillipyosief/alcatel-omniswitch-update-check)](https://galaxy.ansible.com/ui/standalone/roles/phillipyosief/alcatel-omniswitch-update-check/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This Ansible role checks current firmware, FPGA, and U-Boot versions on Alcatel-Lucent OmniSwitch devices and generates inventory files for devices requiring updates.

## Features

- ✅ **Version Checking**: Compares current vs target versions
- ✅ **AOS6/AOS8 Support**: Compatible with both AOS versions  
- ✅ **Inventory Generation**: Creates update inventories automatically
- ✅ **Exclusion Lists**: Support for ignore lists
- ✅ **Multi-Component**: Checks firmware, FPGA, and U-Boot versions

## Requirements

- Ansible 2.1 or higher
- Python 3.6 or higher
- Network access to Alcatel OmniSwitch devices
- Collections: `alcatel.aos8`, `ansible.netcommon`

## Installation

```sh
ansible-galaxy install phillipyosief.alcatel-omniswitch-update-check
```

## Usage Example

```yaml
---
- name: Check for OmniSwitch Updates
  hosts: alcatel_switches
  gather_facts: no
  vars:
    inventory_output: "./update_inventory.yml"
    ignore_list: "./ignore_hosts.txt"
    
  roles:
    - phillipyosief.alcatel-omniswitch-update-check
```

## Author & License

**Phillip Jerome Yosief** – phillip.yosief@stadt-frankfurt.de

Distributed under the MIT license.