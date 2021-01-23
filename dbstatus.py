import ssh_command as ssh
import config
import mysql.connector
from mysql.connector import Error
import Connect_to_db as db


class get_dbstatus():
    def __init__(self):
        self.db_user = config.db_user
        self.db_pass = config.db_pass
        self.master_db = config.master_db
        self.slave1 = config.slave1
        self.slave2 = config.slave2
        self.slave_db_user = config.slave_db_user
        self.slave_db_pass = config.slave_db_pass


    def get_memory_details(self):
        details = ssh.bash_execute("free -m")
        details = details['output'].split(b'\n')[1].decode()
        total = details.split()[1]
        used = details.split()[2]
        free = details.split()[3]
        cached = details.split()[6]
        used_percentage = round((float(used) / float(total)) * 100.0, 2)
        return {"total_memory": total, "used_memory": used, "free_memory": free, "cached_memory": cached, "used_memory_percentage" : used_percentage }


    def get_cpu_details(self):
        load_details = ssh.bash_execute('cat /proc/loadavg')
        load_details = load_details['output'].decode().split()
        server_load = ', '.join([str(item) for item in load_details[:3]])
        cpu_details = ssh.bash_execute("mpstat")
        cpu_details = cpu_details['output'].split(b'\n')
        cpu_cores = cpu_details[0].split(b'\t')[3].decode().strip('(').rstrip(')')
        iow = cpu_details[3].decode().split()[6]
        cpu_idle = float(cpu_details[3].decode().split()[12])
        cpu_used = round(100.0 - cpu_idle, 2)
        return {"server_load": server_load, "cpu_cores": cpu_cores, "iow": iow, "cpu_idle": cpu_idle, "cpu_used": cpu_used}


    def get_mysql_info(self):
        innotop_dashbord = ssh.bash_execute(f"innotop  -u{self.db_user} -p{self.db_pass} --count 1 -d 1 -n --mode A")
        innotop_dashbord = innotop_dashbord['output'].split(b'\n')[1].split(b'\t')
        mysql_uptime = innotop_dashbord[0].decode()
        max_query_time = innotop_dashbord[1].decode()
        if not max_query_time:
            max_query_time = 'N/A'
        mysql_qps = round(float(innotop_dashbord[3].decode()), 2)
        mysql_open_connections = innotop_dashbord[4].decode()
        # locked_count = innotop_dashbord[7].decode()
        innotop_open_tables = ssh.bash_execute(f"innotop -u{self.db_user} -p{self.db_pass} --count 1 -d 1 -n --mode O")
        innotop_open_tables = innotop_open_tables['output'].split(b'\n')
        top_table1 = innotop_open_tables[1].split(b'\t')
        top_table2 = innotop_open_tables[2].split(b'\t')
        if len(top_table1) > 1:
            top_table1_dbname = top_table1[0].decode()
            top_table1_name = top_table1[1].decode()
            top_table1_open_times = top_table1[2].decode()
        else:
            top_table1_dbname = ''
            top_table1_name = ''
            top_table1_open_times = ''
        if len(top_table2) > 1:
            top_table2_dbname = top_table2[0].decode()
            top_table2_name = top_table2[1].decode()
            top_table2_open_times = top_table2[2].decode()
        else:
            top_table2_dbname = ""
            top_table2_name = ""
            top_table2_open_times = ""
        count_cursor = db.connect_to_db(self.master_db,self.db_user, self.db_pass)
        cursor = count_cursor.cursor()
        query = """SELECT count(*) FROM information_schema.PROCESSLIST where COMMAND not in  ('Sleep','Binlog Dump','Daemon')"""
        cursor.execute(query)
        processes = cursor.fetchall()
        process_count = [x[0] for x in processes][0]
        cursor.close()
        count_cursor.close()
        return {"mysql_uptime": mysql_uptime, "max_query_time": max_query_time, "mysql_qps": mysql_qps , "mysql_open_connections": mysql_open_connections,
                "process_count": process_count, "top_table1_dbname":top_table1_dbname, "top_table1_name":top_table1_name,
                "top_table1_open_times": top_table1_open_times, "top_table2_dbname":top_table2_dbname, "top_table2_name": top_table2_name, "top_table2_open_times": top_table2_open_times}


    def get_slaves_info(self):
        cursor_slave1 = db.connect_to_remote_db(self.slave1, self.slave_db_user, self.slave_db_pass)
        cursor = cursor_slave1.cursor()
        cursor.execute("show slave status")
        slave1_details = cursor.fetchall()
        slave1_IO = slave1_details[0][10]
        slave1_SQL = slave1_details[0][11]
        slave1_behind_secs = slave1_details[0][32]
        cursor.close()
        cursor_slave1.close()
        cursor_slave2 = db.connect_to_remote_db(self.slave2, self.slave_db_user, self.slave_db_pass)
        cursor = cursor_slave2.cursor()
        cursor.execute("show slave status")
        slave2_details = cursor.fetchall()
        slave2_IO = slave2_details[0][10]
        slave2_SQL = slave2_details[0][11]
        slave2_behind_secs = slave2_details[0][32]
        cursor.close()
        cursor_slave2.close()

        return {"slave1_IO": slave1_IO, "slave1_SQL":slave1_SQL, "slave1_behind_secs":slave1_behind_secs, "slave2_IO":slave2_IO , "slave2_SQL":slave2_SQL, "slave2_behind_secs":slave2_behind_secs }

