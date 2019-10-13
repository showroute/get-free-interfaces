import re
import getpass

from netmiko import ConnectHandler
from progress.bar import Bar


def connect_to_device(hostname, username, password, secret):
    device = {'device_type':'cisco_ios',
              'host': hostname,
              'username': username,
              'password': password,
              'secret': secret
              }
    return ConnectHandler(**device)

def get_down_interfaces():
    device = connect_to_device(switch, username, password, secret)
    show_int_desc = device.send_command('show interfaces description | in dot1x')
    down_interfaces = []
    print('Looking for free ports...\n')
    for i in show_int_desc.split('\n'):
        match = re.search('(?P<int>Gi\d/\d/\d{1,2}.+?down.+?down.+?dot1x)', i)
        if match:
            down_interfaces.append(match[0].split()[0])
    device.disconnect()
    return down_interfaces

def get_free_interfaces():
    free_interfaces = []
    down_interfaces = get_down_interfaces()
    bar = Bar('Processing', suffix='%(percent)d%%', max=len(down_interfaces))
    device = connect_to_device(switch, username, password, secret)
    for int in down_interfaces:
        show_int = device.send_command('show interface {}'.format(int))
        match = re.search('(?P<packets>0 packets input, 0 bytes, 0 no buffer)', show_int)
        if match:
            free_interfaces.append(int)
        bar.next()
    bar.finish()
    device.disconnect()
    return free_interfaces

def get_uptime():
    print('Definig the switch uptime...')
    device = connect_to_device(switch, username, password, secret)
    return device.send_command('show version | in uptime is')

def main():
    print(get_uptime())
    for i in get_free_interfaces():
        print(i)

if __name__ == "__main__":
    switch = input('Enter switch hostname or ipaddress: ')
    username = input('Enter username: ')
    password = getpass.getpass('Enter password: ')
    secret = getpass.getpass('Enter enable: ')
    main()
