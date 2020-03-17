import ipaddress
import argparse
import os
import jinja2
import configparser


def load_config(conf: str) -> dict:
    """
    Load the contents of .conf file and returns a section
    :param conf: Config section to be retrieved
    :return: contents of a config section
    """
    conf_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.conf')
    c = configparser.ConfigParser()
    c.read(conf_file_path)
    return dict(c[conf])


def read_words(file_path: str) -> list:
    """
    Reads a file and returns the words in it
    :param file_path: Path of the file to be read
    :return: List of words in the file
    """
    with open(file_path, 'r') as f:
        words = f.read().split()

    return words


def generate_addresses(user_names: list, subnet: str, last_used_address: str) -> dict:
    """
    Generates a dictionary of username and ip-address pair dictionary
    :param user_names: List of usernames
    :param subnet: The subnet address
    :param last_used_address: Last used ip-address in existing config
    :return: username and ip-address pair dictionary
    """
    try:
        # Generate hosts
        subnet = ipaddress.ip_network(subnet)
        hosts = subnet.hosts()
        if last_used_address:
            last_used_address = ipaddress.ip_address(last_used_address)
            while last_used_address != next(hosts):
                pass

        return {username: str(next(hosts)) for username in user_names}
    except StopIteration:
        print('Subnet too small')


def render_template(template_path: str, template_name: str, config_variables: dict) -> str:
    """
    Loads and renders a config template
    :param template_path: Templates folder path
    :param template_name: Template name
    :param config_variables: Config variables for rendering the template
    :return: Rendered config
    """
    template_loader = jinja2.FileSystemLoader(searchpath=template_path)
    template_env = jinja2.Environment(loader=template_loader)
    try:
        template = template_env.get_template(template_name)
    except jinja2.exceptions.TemplateNotFound:
        raise FileNotFoundError(f'Template {os.path.join(template_path, template_name)} not found')

    return template.render(**config_variables)


def write_file(folder_path: str, file_name: str, contents: str) -> None:
    """
    Writes a string into a file in a specified folder
    :param folder_path: Folder path
    :param file_name: File name
    :param contents: Contents of the file
    :return: None
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f'Folder {folder_path} not found')
    with open(os.path.join(folder_path, file_name), 'w') as f:
        f.write(contents)


def parse_args():
    # Parsing command line arguments
    parser = argparse.ArgumentParser(description='Generate VPN group policy config')
    parser.add_argument('-u', '--users', type=str, metavar='', required=True,
                        help='Username file')
    parser.add_argument('-c', '--site_code', type=str, metavar='', required=True,
                        help='Site code')
    parser.add_argument('-s', '--subnet', type=str, metavar='', required=True,
                        help='Subnet in /n format')
    parser.add_argument('-g', '--group_policy', type=str, metavar='', required=True,
                        help='Group policy name')
    parser.add_argument('-a', '--auth_server_name', type=str, metavar='', required=True,
                        help='Authentication server name')
    parser.add_argument('-b', '--gateway_base_url', type=str, metavar='', required=True,
                        help='Base gateway URL of the group-url')
    parser.add_argument('-l', '--last_used_address', type=str, metavar='', required=False,
                        help='Last used IP address in existing config')

    args = parser.parse_args()

    # Validating the arguments
    try:
        ipaddress.ip_network(args.subnet)
        if args.last_used_address:
            ipaddress.ip_address(args.last_used_address)
        if not os.path.exists(args.users):
            raise FileNotFoundError(f'{args.users} file not found')
    except Exception as e:
        print(f'Exception occurred. Error in inputs\nDetails {e.__str__()}')

    return args


def main():
    # Load config
    conf = load_config('paths')

    # Parse args
    args = parse_args()

    # Read username file
    user_names = read_words(args.users)

    # Generate address dictionary
    addresses = generate_addresses(user_names, args.subnet, args.last_used_address)

    # Prepare config_variables
    data = {
        'addresses': addresses,
        'group_policy': args.group_policy,
        'auth_server_name': args.auth_server_name,
        'gateway_base_url': args.gateway_base_url,
    }

    # Generate configs
    set_config = render_template(conf['templates_path'], 'POLICY_GROUP_CONFIG', data)
    clear_config = render_template(conf['templates_path'], 'POLICY_GROUP_CLEAR_CONFIG', data)

    # Write result
    write_file(conf['destination_path'], f'set-config-{args.site_code}', set_config)
    write_file(conf['destination_path'], f'clear-config-{args.site_code}', clear_config)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'Exception occurred. Error in generating configs\nDetails {e.__str__()}')
