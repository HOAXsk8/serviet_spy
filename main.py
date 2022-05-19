# main.py

""" This tool was created for security research purposes. It may be used within a network that you have permission to do
so. Any unauthorised attempts to exploit a network using this tool is forbidden. The developer takes no responsibility
for your actions. """

import socket
import csv
import database_functions as db
import psutil
import multiprocessing
import time


def create_ip_list(cidr_ip_range="192.168.1.0/24"):
    """ Take an IP range, iterate hosts 1-254, append host to the IP address and return a new IP for scanning"""
    ip_list = []
    ip = cidr_ip_range.split('.')

    for x in range(1, 254 + 1):  # Iterate through hosts 1 - 254
        ip[-1] = str(x)
        new_ip = ip
        new_ip = '.'.join(ip)
        ip_list.append(new_ip)
    return ip_list


def create_port_list():
    """ Create a list of top TCP and UDP ports """
    file = 'port-numbers.csv'  # Specify the name of the file containing a list of ports
    port_list = []  # List populated by csv file

    with open(file, newline='') as csv_file:
        reader = csv.reader(csv_file, delimiter=' ', quotechar='|')
        for line in reader:
            port_list.append(*line)
    return port_list


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
    """ Get the current CPU and RAM usage percentage """
    processor_usage = psutil.cpu_percent(0.01)  # CPU usage object at 0.1 second intervals
    mem_usage = psutil.virtual_memory()  # Memory usage object
    mem_usage = mem_usage[2]  # Memory usage percentage
    return processor_usage, mem_usage


def worker():
    """ This function defines the task each worker will execute """
    port_list = create_port_list()
    execute = True

    while execute:
        row = db.execute_sql('read', db.SELECT_RANDOM_ROW)
        cidr_ip = row[0][0]
        ip_range = create_ip_list(cidr_ip)
        db.execute_sql('write', db.UPDATE_ROW.format(cidr_ip))  # Update the scanned row (scanned_status = true)

        for ip in ip_range:
            open_ports = []
            for port in port_list:
                open_port = scanner(ip, port)
                if open_port:
                    print(f"[*] Port '{open_port}' found")
                    open_ports.append("{"+open_port+"}")
            if len(open_ports) > 0:
                for i in open_ports:
                    db.execute_sql('write', db.INSERT_SERVICE_DATA.format(ip, i))  # Write open ip:port to database.


def spawn_work_force(MAX_RAM_UTILIZATION=70, MAX_CPU_UTILIZATION=70):  # Set default resource usage
    """ Continuously spawn workers/processes until the max CPU or max RAM usage is reached. """
    spawn_worker = True
    work_force = 0

    while spawn_worker:
        cpu_utilization, ram_utilization = get_system_usage()
        if ram_utilization < MAX_RAM_UTILIZATION and cpu_utilization < MAX_CPU_UTILIZATION:
            process = multiprocessing.Process(target=worker)
            process.start()
            work_force += 1
            print(work_force)
            time.sleep(2)
        else:
            spawn_worker = False
            print(f"CPU used = {cpu_utilization}\nRAM used = {ram_utilization}\nWorkers spawned = {work_force}")


if __name__ == '__main__':
    spawn_work_force(90, 90)
