import config
import mysql.connector
from mysql.connector import Error
import ssh_command
import Connect_to_db as db

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def get_service_status():
    connection = db.connect_to_db(config.master_db, config.db_user, config.db_pass)
    if connection.is_connected():
        cursor = connection.cursor()
        cursor.execute("select host_name,address from workers ")
        result = cursor.fetchall()
        for worekr_name, worker_address in result:
            service_status = ssh_command.remote_bash_execute(worker_address, "systemctl status data_writer")
            buffer_status =  ssh_command.remote_bash_execute(worker_address, "echo 'testing' | nc -U /usr/local/nagios/nagios_data_writer.sock")
            status = f"{bcolors.OKGREEN} Running {bcolors.ENDC}" if 'running' in service_status["output"][2].rstrip('\n') else f"{bcolors.FAIL} Stoped {bcolors.ENDC}"
            buffer = f"{bcolors.OKBLUE} OK {bcolors.ENDC}" if not buffer_status["error"] else f"{bcolors.FAIL} Failed. The socket does not accept any packet.{bcolors.ENDC}"
            print(f"{worekr_name} \t {worker_address}\t{bcolors.BOLD} Service is{bcolors.ENDC} {status} \tTesting socket:{buffer} ")
        cursor.close()
        connection.close()





