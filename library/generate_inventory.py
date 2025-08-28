from ansible.module_utils.basic import AnsibleModule
import yaml
import os

# Wrapper-Klasse für Strings, die immer gequoted werden sollen
class QuotedString(str):
    pass

def quoted_presenter(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')

yaml.add_representer(QuotedString, quoted_presenter)

# Function to read IP addresses from a file into a list
def read_ips(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines()]

def generate_inventory(module):
    # Extract parameters from module
    uboot_file = module.params['uboot_file']
    fpga_file = module.params['fpga_file']
    firmware_file = module.params['firmware_file']
    inventory_file_path = module.params['inventory_file_path']
    ansible_connection = module.params['ansible_connection']
    ansible_network_os = module.params['ansible_network_os']
    ansible_user = module.params['ansible_user']
    ansible_password = module.params['ansible_password']
    ansible_python_interpreter = module.params['ansible_python_interpreter']
    
    # Files list
    aos_toupdate_files = [uboot_file, fpga_file, firmware_file]
    
    # Create the inventory template
    inventory_template = {
        "all": {
            "vars": {
                "ansible_connection": ansible_connection,
                "ansible_network_os": ansible_network_os,
                # als literal Jinja2-Strings für Environment-Variable Lookup
                "ansible_user": QuotedString("{{ lookup('env', 'ANSIBLE_USER') }}"),
                "ansible_password": QuotedString("{{ lookup('env', 'ANSIBLE_PASSWORD') }}"),
                "ansible_python_interpreter": ansible_python_interpreter
            },
            "children": {
                "uboot": {
                    "hosts": {},
                },
                "fpga": {
                    "hosts": {},
                },
                "firmware": {
                    "hosts": {},
                },
            }
        }
    }

    # Load existing inventory file if it exists
    if os.path.exists(inventory_file_path):
        try:
            with open(inventory_file_path, 'r') as yaml_file:
                existing_inventory = yaml.safe_load(yaml_file)
                if existing_inventory and 'all' in existing_inventory:
                    # Merge existing hosts with new template
                    for category in ['uboot', 'fpga', 'firmware']:
                        if (existing_inventory.get('all', {}).get('children', {}).get(category, {}).get('hosts')):
                            inventory_template["all"]["children"][category]["hosts"] = existing_inventory["all"]["children"][category]["hosts"]
        except Exception as e:
            module.fail_json(msg=f"Error loading existing inventory file: {str(e)}")

    # Read IP addresses from files and add to inventory
    hosts_added = 0
    for category, filename in zip(['uboot', 'fpga', 'firmware'], aos_toupdate_files):
        if os.path.exists(filename):
            try:
                ip_addresses = read_ips(filename)
                unique_ips = set(ip_addresses)

                # Add IPs if they're not already in the category
                for ip in unique_ips:
                    if ip not in inventory_template["all"]["children"][category]["hosts"]:
                        inventory_template["all"]["children"][category]["hosts"][ip] = {}
                        hosts_added += 1
            except Exception as e:
                module.fail_json(msg=f"Error reading file {filename}: {str(e)}")
        else:
            # Warning, but no error
            pass

    # Save the inventory as YAML file
    try:
        with open(inventory_file_path, 'w') as yaml_file:
            yaml.dump(
                inventory_template,
                yaml_file,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
                width=1000
            )
    except Exception as e:
        module.fail_json(msg=f"Error saving inventory file: {str(e)}")

    return inventory_template, hosts_added

def main():
    module = AnsibleModule(
        argument_spec=dict(
            uboot_file=dict(type='str', required=False, default='/home/user/temp/aos_toupdate_uboot'),
            fpga_file=dict(type='str', required=False, default='/home/user/temp/aos_toupdate_fpga'),
            firmware_file=dict(type='str', required=False, default='/home/user/temp/aos_toupdate_firmware'),
            inventory_file_path=dict(type='str', required=False, default='/home/user/temp/aos_toupdate.yml'),
            ansible_connection=dict(type='str', required=False, default='ansible.netcommon.network_cli'),
            ansible_network_os=dict(type='str', required=False, default='alcatel.aos8.aos8'),
            ansible_user=dict(type='str', required=False, default='{{ ansible_user }}'),
            ansible_password=dict(type='str', required=False, default='{{ ansible_password }}', no_log=True),
            ansible_python_interpreter=dict(type='str', required=False, default='/usr/bin/python3'),
        ),
        supports_check_mode=True
    )

    if module.check_mode:
        # In check mode, only simulate
        module.exit_json(changed=False, msg="Check mode: Inventory would be generated")

    try:
        inventory, hosts_added = generate_inventory(module)
        
        # Determine if changes were made
        changed = hosts_added > 0
        
        module.exit_json(
            changed=changed,
            inventory_file=module.params['inventory_file_path'],
            hosts_added=hosts_added,
            inventory=inventory,
            msg=f"Inventory successfully generated. {hosts_added} new hosts added."
        )
        
    except Exception as e:
        module.fail_json(msg=f"Unexpected error: {str(e)}")

if __name__ == '__main__':
    main()
