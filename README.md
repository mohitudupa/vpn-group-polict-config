# Tool to generate group policy configs for employee and extranet vpn headends

## Setup and install

- Requires python version 3

- Install the packages with
    ```
    pip install -r requirements.txt
    ```

- Edit the .conf file in the project root to point to the appropriate templates folder and destination folder


## Running the script
Script to generate vpn config
In the default configuration, run the script in the project root folder

The usernames must be stored in a file, separated by newlines or spaces
```
python generate_group_policy_config.py -u <usernames_file> -c <site_code> -s <subnet_address> -l <last_used_address> -g <group_policy_name> -a <auth_server_name> -b <gateway_base_url>
```

Run the following for help in the arguments
```
python generate_group_policy_config.py --help

usage: generate_group_policy_config.py [[-h] -u  -c  -s  -g  -a  -b  [-l]

Generate VPN group policy config

optional arguments:
  -h, --help            show this help message and exit
  -u , --users          Username file
  -c , --site_code      Site code
  -s , --subnet         Subnet in /n format
  -g , --group_policy   Group policy name
  -a , --auth_server_name
                        Authentication server name
  -b , --gateway_base_url
                        Base gateway URL of the group-url
  -l , --last_used_address
                        Last used IP address in existing config

```


## Config Templates
The config templates for creating and removing vpn group policies can be found in vpn/templates

The templates use standard jinja syntax

Create Config
```
{% for username, ip_address in addresses.items() %}
    ip local pool {{ username }} {{ ip_address }} mask 255.255.255.255
    tunnel-group {{ username }} type remote-access
    tunnel-group {{ username }} general-attributes
    address-pool {{ username }}
    authentication-server-group {{ auth_server_name }}
    default-group-policy {{ group_policy }}
    tunnel-group {{ username }} webvpn-attributes
    group-url {{ gateway_base_url }}{{ username }} enable
{% endfor %}
```

Clear Config
```
{% for username in addresses.keys() %}
    clear configure tunnel-group {{username}}
    no ip local pool {{username}}
{% endfor %}
```