# main.py

""" This tool was created for research purposes only. It can be used to gather information about software used on
protocols specified by the user. This tool will not exploit anything, however, it will continuously scan random IP's and
momentarily establish a connection to a listening port and listen for a response.
Use at your own risk! """

import socket
import csv
import database_functions as db
from itertools import product
import sys


def get_ip_range(ip):
    ip_list = []

    for x in range(1, 255):
        ip = ip.split('.')
        ip[-1] = str(x)
        ip = '.'.join(ip)
        ip_list.append(ip)
    return ip_list


def create_port_list():
    """ Create a list of top TCP and UDP ports """
    top_ports = []  # List populated by csv file upon program execution, 1800+ ports

    with open('top-ports.csv', newline='') as csv_file:
        reader = csv.reader(csv_file, delimiter=' ', quotechar='|')
        for line in reader:
            top_ports.append(*line)
    return top_ports


def scanner(ip, port, TIMEOUT=0.2):
    """ Connect to a given host and port, append (ip, port) to tuple and return. """

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(TIMEOUT)
        connection = s.connect_ex((ip, int(port)))
        if connection == 0:
            print(f'[+] {str(ip)}:{str(port)}')
            return port
        else:
            pass
    except socket.timeout:
        pass
    except socket.error:
        pass


def worker():
    execute = True
    port_list = create_port_list()
    row = db.execute_sql('read', db.SELECT)

    while execute:
        cidr_ip = row[0][0]
        ip_range = get_ip_range(cidr_ip)

        for ip, port in product(ip_range, port_list):  # Loop through each IP scanning each port in the list
            open_port = scanner(ip, port)
            if open_port:
                print(f'{ip}:{open_port}')
                db.execute_sql('write', db.INSERT.format(ip, open_port))  # Write open ip:port to database.

        db.execute_sql('write', db.UPDATE.format(cidr_ip))  # Update the scanned row (scanned_status = true)


if __name__ == '__main__':
    worker()
