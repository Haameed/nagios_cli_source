import curses
from curses import error
import dbstatus
import config
import workers
import datetime
import time



end_epoch_time = int(round(time.time())) + config.auto_kill_minutes * 60
end_datetime = datetime.datetime.now() + datetime.timedelta(minutes=config.auto_kill_minutes)
def dbstatus_main():
    curses.wrapper(dbstatus_screen)

def workers_main():
    curses.wrapper(worker_screen)

def dbstatus_screen(screen):
    try:

    # screen = curses.initscr()
    # curses.start_color()
        curses.noecho()
        curses.cbreak()
        screen.keypad(True)
        curses.curs_set(0)
        rows, cols = screen.getmaxyx()
        screen.refresh()
        starting_line = 1
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)  # cyan for titles:
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # green for OK or  messages
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # yellow for warning
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)  # red for critical
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # magenta for secondary titles messages
        screen.clear()
        screen.border('|', '|', '-', '-', '+', '+', '+', '+',)
        mem_info = dbstatus.get_dbstatus().get_memory_details()
        total_memory = mem_info["total_memory"]
        used_memory = mem_info["used_memory"]
        free_memory = mem_info["free_memory"]
        cached_memory = mem_info["cached_memory"]
        used_memory_percentage = mem_info["used_memory_percentage"]
        cpu = dbstatus.get_dbstatus().get_cpu_details()
        server_load = cpu["server_load"]
        cpu_cores = cpu["cpu_cores"]
        iow = cpu["iow"]
        cpu_idle = cpu["cpu_idle"]
        cpu_used = cpu["cpu_used"]
        mysql_info = dbstatus.get_dbstatus().get_mysql_info()
        mysql_uptime = mysql_info["mysql_uptime"]
        max_query_time = mysql_info["max_query_time"]
        mysql_qps = mysql_info["mysql_qps"]
        mysql_open_connections = mysql_info["mysql_open_connections"]
        process_count = mysql_info["process_count"]
        top_table1_dbname = mysql_info["top_table1_dbname"]
        top_table1_name = mysql_info["top_table1_name"]
        top_table1_open_times = mysql_info["top_table1_open_times"]
        top_table2_dbname = mysql_info["top_table2_dbname"]
        top_table2_name = mysql_info["top_table2_name"]
        top_table2_open_times = mysql_info["top_table2_open_times"]
        slaves = dbstatus.get_dbstatus().get_slaves_info()
        slave1_IO = slaves["slave1_IO"]
        slave1_SQL = slaves["slave1_SQL"]
        slave1_behind_secs = slaves["slave1_behind_secs"]
        slave2_IO = slaves["slave2_IO"]
        slave2_SQL = slaves["slave2_SQL"]
        slave2_behind_secs = slaves["slave2_behind_secs"]
        finish_in = str(end_datetime - datetime.datetime.now()).split('.')[0]
        screen.addstr(starting_line, 2, "nagios database status:", curses.A_BOLD + curses.color_pair(2))
        screen.addstr(starting_line, 30, f"{time.strftime('%Y-%m-%d %H:%M:%S')}", + curses.A_BOLD + curses.color_pair(2))
        screen.addstr(starting_line + 1, 2, "---------------------------------------------------", curses.A_BOLD + curses.color_pair(2))
        screen.addstr(starting_line + 2, 2, "Server status:", curses.color_pair(1))
        screen.addstr(starting_line + 4, 4, "Memory details:", curses.color_pair(5))
        if used_memory_percentage < float(config.warning_threshold):
            color_code = curses.color_pair(0)
        elif float(config.warning_threshold) <= used_memory_percentage < float(config.critical_threshold):
            color_code = curses.color_pair(3) + curses.A_BLINK
        else:
            color_code = curses.color_pair(4) + curses.A_BLINK
        screen.addstr(starting_line + 6, 8, f"Total Mem: {total_memory} MB", curses.color_pair(0))
        screen.addstr(starting_line + 6, 32, f"Free: {free_memory} MB", curses.color_pair(0))
        screen.addstr(starting_line + 6, 50, f"Cached: {cached_memory} MB", curses.color_pair(0))
        screen.addstr(starting_line + 6, 70, f"Used: {used_memory} MB = {used_memory_percentage}%", color_code)
        screen.addstr(starting_line + 8, 4, "CPU details:", curses.color_pair(5))
        screen.addstr(starting_line + 10, 8, f"Total cores: {cpu_cores}")
        if cpu_used < float(config.warning_threshold):
            color_code = curses.color_pair(0)
        elif float(config.warning_threshold) <= cpu_used < float(config.critical_threshold):
            color_code = curses.color_pair(3) + curses.A_BLINK
        else:
            color_code = curses.color_pair(4) + curses.A_BLINK
        screen.addstr(starting_line + 10, 32, f"Used: {cpu_used}%", color_code)
        screen.addstr(starting_line + 10, 50, f"Idle: {cpu_idle}%", curses.color_pair(0))
        screen.addstr(starting_line + 10, 67, f"iow: {iow},	Load Avg: {server_load}")
        screen.addstr(starting_line + 12, 4, "mysql status:", curses.color_pair(5))
        screen.addstr(starting_line + 14, 8, "uptime:")
        screen.addstr(starting_line + 14, 30, f"{mysql_uptime}")
        screen.addstr(starting_line + 14, 40, "days")
        screen.addstr(starting_line + 14, 51, "| Slave1:")
        screen.addch(starting_line + 15, 51, "|")
        screen.addstr(starting_line + 15, 57, f"I/O Running: {slave1_IO}",
                      curses.color_pair(4) + curses.A_BLINK if slave1_IO != "Yes" else curses.color_pair(0))
        screen.addch(starting_line + 16, 51, "|")
        screen.addstr(starting_line + 16, 57, f"SQL Running: {slave1_SQL}",
                      curses.color_pair(4) + curses.A_BLINK if slave1_SQL != "Yes" else curses.color_pair(0))
        screen.addstr(starting_line + 17, 51, f"|     Time behind: {slave1_behind_secs} s")
        screen.addstr(starting_line + 18, 51, "| Slave2:")
        screen.addch(starting_line + 19, 51, "|")
        screen.addstr(starting_line + 19, 57, f"I/O Running: {slave2_IO}",
                      curses.color_pair(4) + curses.A_BLINK if slave2_IO != "Yes" else curses.color_pair(0))
        screen.addch(starting_line + 20, 51, "|")
        screen.addstr(starting_line + 20, 57, f"SQL Running: {slave2_SQL}",
                      curses.color_pair(4) + curses.A_BLINK if slave2_SQL != "Yes" else curses.color_pair(0))
        screen.addstr(starting_line + 21, 51, f"|     Time behind: {slave2_behind_secs} s")
        if process_count < config.warning_threshold:
            color_code = curses.color_pair(0)
        elif float(config.processes_warning) <= process_count < float(config.processes_warning):
            color_code = curses.color_pair(3) + curses.A_BLINK
        else:
            color_code = curses.color_pair(4) + curses.A_BLINK
        screen.addstr(starting_line + 15, 8, "queries:")
        screen.addstr(starting_line + 15, 30, f"{mysql_qps}")
        screen.addstr(starting_line + 15, 40, "qps")
        screen.addstr(starting_line + 16, 8, "Max query time:")
        screen.addstr(starting_line + 16, 30, f"{max_query_time}")
        screen.addstr(starting_line + 16, 40, "seconds")
        screen.addstr(starting_line + 17, 8, "Connections:")
        screen.addstr(starting_line + 17, 30, f"{mysql_open_connections}")
        screen.addstr(starting_line + 18, 8, "current processes:", color_code)
        screen.addstr(starting_line + 18, 30, f"{process_count}", color_code)
        screen.addstr(starting_line + 19, 8, "Top open table:")
        screen.addstr(starting_line + 20, 10, "db name:")
        screen.addstr(starting_line + 20, 24, "table name")
        screen.addstr(starting_line + 20, 44, "times")
        screen.addstr(starting_line + 21, 10, f"{top_table1_dbname}")
        screen.addstr(starting_line + 21, 24, f"{top_table1_name}")
        screen.addstr(starting_line + 21, 48, f"{top_table1_open_times}")
        screen.addstr(starting_line + 22, 10, f"{top_table2_dbname}")
        screen.addstr(starting_line + 22, 24, f"{top_table2_name}")
        screen.addstr(starting_line + 22, 48, f"{top_table2_open_times}")
        screen.refresh()
        message_win = curses.newwin(3, 90, rows - 4, 1)
        message_win.box()
        message_win.addstr(1, 1, f"press 'ctrl + c' to exit the program.the program will exit automaticaly in {finish_in}.", curses.A_BOLD + curses.color_pair(1))
        message_win.refresh()

        curses.napms(1000)

    except error as e:
        time.sleep(1)
        dbstatus_main()

def worker_screen(screen):
    try:
        workers_status = workers.workers_status()
        curses.noecho()
        curses.cbreak()
        screen.keypad(True)
        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)  # cyan for titles:
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # green for OK or  messages
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # yellow for warning
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)  # red for critical
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # magenta for secondary titles messages
        rows, cols = screen.getmaxyx()
        screen.clear()
        screen.border(0)
        screen.addstr(1, 2, "Nagios Workers status:", curses.A_BOLD + curses.color_pair(2))
        screen.addstr(1, 30, f"{time.strftime('%Y-%m-%d %H:%M:%S')}",
                      + curses.A_BOLD + curses.color_pair(2))
        screen.addstr(2, 2, "---------------------------------------------------",
                      curses.A_BOLD + curses.color_pair(2))
        """ creating host check window"""
        screen.addch(4, 5, "+")
        screen.addstr(4, 13, "Updated Hosts", curses.A_BOLD + curses.color_pair(5))
        screen.addch(4, 34, "+")
        screen.refresh()
        host_box = curses.newwin(22, 30, 5, 5)
        host_box.box()
        line = 1
        for srv_count, srv_update in workers_status["hosts"]:
            host_box.addstr(line, 2, f"{srv_count}", curses.color_pair(1))
            host_box.addch(line, 9, "|")
            host_box.addstr(line, 11, f"{srv_update}", curses.color_pair(1))
            line += 1
        screen.addch(27, 5, "+")
        screen.addstr(27, 8, "Checks older than 20 min", curses.A_BOLD + curses.color_pair(3))
        screen.addch(27, 34, "+")
        host_old_check = curses.newwin(3, 30, 28, 5)
        host_old_check.box()
        row_color = (curses.color_pair(4) + curses.A_BLINK if workers_status['delayed_hosts'][0][0] > config.old_checks_threshold else curses.color_pair(3))
        host_old_check.addstr(1, 2, f"{workers_status['delayed_hosts'][0][0]}", row_color)
        host_old_check.addch(1, 9, f"|")
        host_old_check.addstr(1, 11, f"{workers_status['delayed_hosts'][0][1]}", row_color)
        host_old_check.refresh()
        host_box.refresh()
        """ creating service check window"""
        screen.addch(4, 36, "+")
        screen.addstr(4, 44, "Updated Services", curses.A_BOLD + curses.color_pair(5))
        screen.addch(4, 65, "+")
        screen.refresh()
        service_box = curses.newwin(22, 30, 5, 36)
        service_box.box()
        line = 1
        for srv_count, srv_update in workers_status["services"]:
            service_box.addstr(line, 2, f"{srv_count}", curses.color_pair(1))
            service_box.addch(line, 9, "|")
            service_box.addstr(line, 11, f"{srv_update}", curses.color_pair(1))
            line += 1
        service_box.refresh()
        screen.addch(27, 36, "+")
        screen.addstr(27, 39, "Checks older than 20 min", curses.A_BOLD + curses.color_pair(3))
        screen.addch(27, 65, "+")
        service_old_check = curses.newwin(3, 30, 28, 36)
        service_old_check.box()
        row_color = (curses.color_pair(4) + curses.A_BLINK if workers_status['delayed_services'][0][0] > config.old_checks_threshold else curses.color_pair(3))
        service_old_check.addstr(1, 2, f"{workers_status['delayed_services'][0][0]}", row_color)
        service_old_check.addch(1, 9, f"|")
        service_old_check.addstr(1, 11, f"{workers_status['delayed_services'][0][1]}", row_color)
        service_old_check.refresh()
        """ creating a window to show old check by workers"""
        if workers_status["workers_delayed_checks"]:
            screen.addch(4, 67, '+')
            screen.addstr(4, 73, "Old check by workers", curses.A_BOLD + curses.color_pair(5))
            screen.addch(4, 97, '+')
            workers_box = curses.newwin(22, 31, 5, 67)
            workers_box.box()
            line = 1
            for check_count, worker_name in workers_status["workers_delayed_checks"]:
                workers_box.addstr(line, 2, str(check_count), curses.color_pair(1))
                workers_box.addch(line, 8, "|")
                workers_box.addstr(line, 10, worker_name, curses.color_pair(1))
                line += 1
            workers_box.refresh()
        screen.refresh()
        finish_in = str(end_datetime - datetime.datetime.now()).split('.')[0]
        message_win = curses.newwin(3, 90, rows - 4, 1)
        message_win.box()
        message_win.addstr(1, 1, f"press 'ctrl + c' to exit the program.the program will exit automaticaly in {finish_in}.", curses.A_BOLD + curses.color_pair(1))
        message_win.refresh()
        curses.napms(3000)

    except error as e:
        time.sleep(3)
        workers_main()

