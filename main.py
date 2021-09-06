# main.py

""" This tool was created for security research purposes. It can be used to gather information about software used on
protocols specified by the user. This tool will not exploit anything, however, it will continuously scan random IP's and
momentarily establish a connection to a listening port and listen for a response. """

import socket
import csv
import database_functions as db
import psutil
import multiprocessing


def get_ip_list(cidr_ip_range):
    """ Take an IP range, iterate hosts 1-254, append host to the IP address and return a new IP for scanning """
    ip_list = []

    for x in range(1, 254 + 1):  # Iterate through hosts 1 - 254
        ip = cidr_ip_range.split('.')
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
    """ Attempt to Connect to a given host and port. Return open port """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(TIMEOUT)
        connection = s.connect_ex((ip, int(port)))
        if connection == 0:
            return port
        else:
            pass
    except socket.timeout:
        pass
    except socket.error:
        pass


def get_system_usage():
    processor_usage = psutil.cpu_percent(0.01)  # CPU usage object at 0.1 second intervals
    mem_usage = psutil.virtual_memory()  # Memory usage object
    mem_usage = mem_usage[2]  # Memory % usage
    return processor_usage, mem_usage


def worker():
    """ This function defines the task each worker will execute """
    port_list = create_port_list()
    execute = True

    while execute:
        row = db.execute_sql('read', db.SELECT_RANDOM_ROW)
        cidr_ip = row[0][0]
        ip_range = get_ip_list(cidr_ip)

        for ip in ip_range:
            for port in port_list:
                # print(f'{ip}:{port}')
                open_port = scanner(ip, port)
                if open_port:
                    db.execute_sql('write', db.INSERT_SERVICE_DATA.format(ip, open_port))  # Write open ip:port to database.

            db.execute_sql('write', db.UPDATE_ROW.format(cidr_ip))  # Update the scanned row (scanned_status = true)


def spawn_work_force(max_cpu_utilization=50, max_ram_utilization=50):  # Set default resource usage
    """ Continuously spawn workers/processes until the max CPU or max RAM usage is reached. """
    spawn_worker = True
    work_force = 0

    while spawn_worker:
        cpu_utilization, ram_utilization = get_system_usage()
        if cpu_utilization < max_cpu_utilization and ram_utilization < max_ram_utilization:
            print(ram_utilization)
            process = multiprocessing.Process(target=worker)
            process.start()
            work_force += 1
        else:
            spawn_worker = False
            print(f'CPU used: {cpu_utilization}%')
            print(f'Memory used: {ram_utilization}%')
            print(f'Active workers: {work_force}')


if __name__ == '__main__':
    spawn_work_force(70, 70)
