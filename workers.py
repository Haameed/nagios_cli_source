import config
import mysql.connector
from mysql.connector import Error
import Connect_to_db as db


def workers_status():
    connection = db.connect_to_db(config.master_db, config.db_user, config.db_pass)
    cursor = connection.cursor()
    updated_hosts_query = """select count(*), substring(last_update,1,16) as "DATETIME" from (select host_name, last_update from host_monitor union all select host_name, last_update from host_monitor_p2p) as all_hosts where last_update >= adddate(now(), interval -20 minute) group by DATETIME order by DATETIME desc"""
    delayed_hosts_query = """select count(*), max(substring(last_update,1,16)) as "DATETIME" from (select host_name, last_update from host_monitor union all select host_name, last_update from host_monitor_p2p) as all_hosts where last_update < adddate(now(), interval -20 minute)"""
    updated_services_query= """select count(*), substring(last_update,1,16) as "DATETIME" from (select host_name, last_update from service_monitor union all select host_name, last_update from service_monitor_p2p) as all_hosts where last_update >= adddate(now(), interval -20 minute) group by DATETIME order by DATETIME desc """
    delayed_services_query = """select count(*), max(substring(last_update,1,16)) as "DATETIME" from (select host_name, last_update from service_monitor union all select host_name, last_update from service_monitor_p2p) as all_hosts where last_update < adddate(now(), interval -20 minute)"""
    workers_delayed_checks_query = """select count(*) as "items" , value from tbl_variabledefinition where id in (select idSlave from tbl_lnkHostToVariabledefinition where idMaster in (select id from tbl_host where host_name in (select host_name  from (select host_name, last_update from host_monitor union all select host_name, last_update from host_monitor_p2p union all select host_name, last_update from service_monitor union all select host_name, last_update from service_monitor_p2p ) as all_checks where last_update < adddate(now(), interval -20 minute)))) group by value order by items desc limit 20"""
    cursor.execute(updated_hosts_query)
    updated_hosts = cursor.fetchall()
    cursor.execute(updated_services_query)
    updated_services = cursor.fetchall()
    cursor.execute(delayed_hosts_query)
    delayed_hosts = cursor.fetchall()
    cursor.execute(delayed_services_query)
    delayed_services = cursor.fetchall()
    cursor.execute(workers_delayed_checks_query)
    workers_delayed_checks = cursor.fetchall()
    cursor.close()
    connection.close()
    return {"hosts": updated_hosts, "delayed_hosts": delayed_hosts, "services": updated_services, "delayed_services": delayed_services, "workers_delayed_checks": workers_delayed_checks}



